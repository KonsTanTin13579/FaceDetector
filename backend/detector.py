import os
import cv2
import sys
import torch
import numpy as np
from PIL import Image
from sklearn.cluster import DBSCAN
from PyQt5.QtWidgets import (QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from facenet_pytorch import InceptionResnetV1
from retinaface import RetinaFace


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    detection_complete = pyqtSignal(list)

    def __init__(self, video_path, face_rec_model, device):
        super().__init__()
        self.video_path = video_path
        self.face_rec_model = face_rec_model
        self.device = device
        self._run_flag = True
        self.face_positions = []

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0

        while self._run_flag and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Детекция лиц с RetinaFace
            faces = RetinaFace.detect_faces(frame)

            if isinstance(faces, dict):
                for face_id, face_info in faces.items():
                    try:
                        facial_area = face_info['facial_area']
                        x1, y1, x2, y2 = facial_area
                        landmarks = face_info['landmarks']

                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                        if x2 > x1 and y2 > y1:
                            face_img = frame[y1:y2, x1:x2]
                            if face_img.size > 0:
                                # Конвертируем изображение и переносим на то же устройство, что и модель
                                face_pil = Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)).resize((160, 160))
                                face_tensor = torch.tensor(np.array(face_pil) / 255.0).permute(2, 0, 1).unsqueeze(0).float()
                                face_tensor = face_tensor.to(self.device)  # Переносим на правильное устройство

                                with torch.no_grad():
                                    embedding = self.face_rec_model(face_tensor).cpu().numpy()

                                self.face_positions.append({
                                    'frame': frame_count,
                                    'time': frame_count / frame_rate,
                                    'bbox': [x1, y1, x2 - x1, y2 - y1],
                                    'embedding': embedding
                                })

                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                                # Рисуем landmarks
                                for landmark_name, point in landmarks.items():
                                    cv2.circle(frame, tuple(map(int, point)), 2, (0, 0, 255), -1)
                    except Exception as e:
                        print(f"Error processing face: {e}")

            self.change_pixmap_signal.emit(frame)
            frame_count += 1

        cap.release()
        self.detection_complete.emit(self.face_positions)

    def stop(self):
        self._run_flag = False
        self.wait()


class FaceDetectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Detector (RetinaFace)")
        self.setGeometry(100, 100, 800, 600)

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")

        # Модель для извлечения признаков
        self.face_rec_model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        self.btn_open = QPushButton("Open Video", self)
        self.btn_open.clicked.connect(self.open_video)

        self.btn_start = QPushButton("Start Detection", self)
        self.btn_start.clicked.connect(self.start_detection)
        self.btn_start.setEnabled(False)

        self.btn_stop = QPushButton("Stop", self)
        self.btn_stop.clicked.connect(self.stop_detection)
        self.btn_stop.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_open)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        self.setLayout(layout)

        self.thread = None
        self.output_dir = "detected_faces"
        os.makedirs(self.output_dir, exist_ok=True)

    def open_video(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi)")
        if filepath:
            self.video_path = filepath
            self.btn_start.setEnabled(True)

            cap = cv2.VideoCapture(filepath)
            ret, frame = cap.read()
            if ret:
                self.display_frame(frame)
            cap.release()

    def start_detection(self):
        if hasattr(self, 'video_path'):
            self.btn_open.setEnabled(False)
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)

            self.thread = VideoThread(self.video_path, self.face_rec_model, self.device)
            self.thread.change_pixmap_signal.connect(self.display_frame)
            self.thread.detection_complete.connect(self.on_detection_complete)
            self.thread.start()

    def stop_detection(self):
        if self.thread:
            self.thread.stop()
            self.btn_open.setEnabled(True)
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)

    def on_detection_complete(self, face_positions):
        if not face_positions:
            print("No faces detected")
            return

        embeddings = np.vstack([f['embedding'] for f in face_positions])
        clt = DBSCAN(metric="euclidean", eps=0.6, min_samples=2)
        labels = clt.fit_predict(embeddings)

        cap = cv2.VideoCapture(self.video_path)
        for i, label in enumerate(labels):
            info = face_positions[i]
            cluster_dir = os.path.join(self.output_dir, f"person_{label}")
            os.makedirs(cluster_dir, exist_ok=True)

            filename = os.path.join(cluster_dir, f"frame_{info['frame']}.jpg")
            if not os.path.exists(filename):
                cap.set(cv2.CAP_PROP_POS_FRAMES, info['frame'])
                ret, frame = cap.read()
                if ret:
                    x, y, w, h = info['bbox']
                    face_crop = frame[y:y + h, x:x + w]
                    if face_crop.size > 0:
                        cv2.imwrite(filename, face_crop)

        cap.release()
        print(f"Saved {len(face_positions)} faces to {self.output_dir}")
        self.btn_open.setEnabled(True)
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)

    def display_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        if hasattr(self, 'thread') and self.thread:
            self.thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceDetectorApp()
    window.show()
    sys.exit(app.exec_())