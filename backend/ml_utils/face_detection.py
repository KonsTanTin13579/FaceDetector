import cv2
import numpy as np
from retinaface import RetinaFace

class FaceDetector:
    def __init__(self):
        self.detector = RetinaFace

    def detect_faces(self, frame):
        """Обнаружение лиц в кадре"""
        faces = self.detector.detect_faces(frame)
        results = []
        
        if isinstance(faces, dict):
            for face_id, face_info in faces.items():
                facial_area = face_info['facial_area']
                landmarks = face_info['landmarks']
                
                x1, y1, x2, y2 = facial_area
                results.append({
                    'bbox': [x1, y1, x2, y2],
                    'landmarks': landmarks
                })
        
        return results