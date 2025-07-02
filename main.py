import torch
from facenet_pytorch import MTCNN as MTCNN_FT, InceptionResnetV1
import cv2
import numpy as np
from PIL import Image
import os
from sklearn.cluster import DBSCAN
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Используется устройство: {device}")

model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
mtcnn = MTCNN_FT(keep_all=True, device=device)


video_path = 'input_video.mp4'
output_dir = 'detected_faces'
os.makedirs(output_dir, exist_ok=True)

cap = cv2.VideoCapture(video_path)
frame_rate = cap.get(cv2.CAP_PROP_FPS)
frame_count = 0
all_embeddings = []
face_positions = []

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_frame)

    boxes, _ = mtcnn.detect(pil_img)

    if boxes is not None:
        for box in boxes:
            try:
                x1, y1, x2, y2 = box.astype(int)
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(frame.shape[1], x2)
                y2 = min(frame.shape[0], y2)

                face_img = rgb_frame[y1:y2, x1:x2]

                if face_img.size == 0 or face_img.shape[0] < 20 or face_img.shape[1] < 20:
                    continue

                face_pil = Image.fromarray(face_img).resize((160, 160))
                face_tensor = torch.tensor(np.array(face_pil) / 255.0)
                face_tensor = face_tensor.permute(2, 0, 1).unsqueeze(0).float().to(device)

                with torch.no_grad():
                    embedding = model(face_tensor).cpu().numpy()

                all_embeddings.append(embedding)
                face_positions.append({
                    'frame': frame_count,
                    'time': frame_count / frame_rate,
                    'bbox': [x1, y1, abs(x2 - x1), abs(y2 - y1)],  # x, y, width, height
                    'id': None
                })

            except Exception as e:
                print(f"Ошибка обработки лица: {e}")
                continue

    frame_count += 1

cap.release()

if not all_embeddings:
    print("Лица не найдены.")
    exit()


embeddings_stack = np.vstack(all_embeddings)
clt = DBSCAN(metric="euclidean", eps=0.6, min_samples=2)
clt.fit(embeddings_stack)

for i, label in enumerate(clt.labels_):
    face_positions[i]['id'] = label


cap = cv2.VideoCapture(video_path)
for idx, info in enumerate(face_positions):
    face_id = info['id']
    frame_num = info['frame']
    x, y, w, h = info['bbox']

    cluster_dir = os.path.join(output_dir, f"person_{face_id}")
    os.makedirs(cluster_dir, exist_ok=True)

    filename = os.path.join(cluster_dir, f"frame_{frame_num}.jpg")

    if not os.path.exists(filename):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if ret:
            x1, y1 = x, y
            x2, y2 = x + w, y + h


            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(frame.shape[1], x2)
            y2 = min(frame.shape[0], y2)

            if x2 > x1 and y2 > y1:
                face_crop = frame[y1:y2, x1:x2]
                if face_crop.size > 0:
                    cv2.imwrite(filename, face_crop)
                else:
                    print(f"Пустое изображение для {filename}")
            else:
                print(f"Некорректные координаты: {x1}, {y1}, {x2}, {y2}")
        else:
            print(f"Не удалось прочитать кадр {frame_num}")
cap.release()

import torch
from facenet_pytorch import MTCNN as MTCNN_FT, InceptionResnetV1
import cv2
import numpy as np
from PIL import Image
import os
from sklearn.cluster import DBSCAN
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt


class FaceDetectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Detector")
        self.setGeometry(100, 100, 800, 600)

        # Инициализация моделей
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        self.mtcnn = MTCNN_FT(keep_all=True, device=self.device)

        # Элементы интерфейса
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        self.btn_open = QPushButton("Open Video", self)
        self.btn_open.clicked.connect(self.open_video)

        self.btn_start = QPushButton("Start Detection", self)
        self.btn_start.clicked.connect(self.start_detection)
        self.btn_start.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_open)
        layout.addWidget(self.btn_start)
        self.setLayout(layout)

        # Переменные для обработки видео
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.face_positions = []
        self.frame_rate = 30
        self.current_frame = 0

    def open_video(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi)")
        if filepath:
            self.cap = cv2.VideoCapture(filepath)
            self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
            self.btn_start.setEnabled(True)

            # Показать первый кадр
            ret, frame = self.cap.read()
            if ret:
                self.display_frame(frame)

    def start_detection(self):
        if self.cap is None:
            return

        self.btn_open.setEnabled(False)
        self.btn_start.setEnabled(False)

        # Сбросить видео на начало
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.current_frame = 0
        self.face_positions = []

        # Начать обработку
        self.timer.start(1000 // self.frame_rate)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.process_faces()
            return

        self.current_frame += 1
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_frame)

        # Обнаружение лиц
        boxes, _ = self.mtcnn.detect(pil_img)

        if boxes is not None:
            for box in boxes:
                try:
                    x1, y1, x2, y2 = box.astype(int)
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                    if x2 <= x1 or y2 <= y1:
                        continue

                    face_img = rgb_frame[y1:y2, x1:x2]
                    if face_img.size == 0:
                        continue

                    # Сохраняем информацию о лице
                    self.face_positions.append({
                        'frame': self.current_frame,
                        'bbox': [x1, y1, x2 - x1, y2 - y1]
                    })

                    # Рисуем рамку
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                except Exception as e:
                    print(f"Error processing face: {e}")

        self.display_frame(frame)

    def process_faces(self):
        if not self.face_positions:
            print("No faces detected")
            return

        # Здесь можно добавить кластеризацию и сохранение лиц
        print(f"Detected {len(self.face_positions)} faces")
        self.btn_open.setEnabled(True)
        self.btn_start.setEnabled(True)

    def display_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        if self.cap is not None:
            self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceDetectorApp()
    window.show()
    sys.exit(app.exec_())