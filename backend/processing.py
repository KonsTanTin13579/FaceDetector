import os
import cv2
import time
import uuid
import numpy as np
from pathlib import Path
from .ml_utils.face_detection import FaceDetector
from .ml_utils.face_recognition import FaceRecognizer
from .ml_utils.age_gender import AgeGenderPredictor
from .database import get_session
from .models import VideoProcessing, Face

face_detector = FaceDetector()
face_recognizer = FaceRecognizer()
age_gender_predictor = AgeGenderPredictor()

async def process_video(video_id: str, file_path: str):
    """Основная функция обработки видео"""
    start_time = time.time()

    async with get_session() as session:
        video_record = await session.get(VideoProcessing, video_id)
        video_record.status = "processing"
        await session.commit()
    
    try:
        cap = cv2.VideoCapture(file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = 0
     
        all_faces = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % int(fps) != 0:
                continue
            
            detected_faces = face_detector.detect_faces(frame)
            current_time = frame_count / fps
            
            for face in detected_faces:
                x1, y1, x2, y2 = map(int, face['bbox'])
                face_img = frame[y1:y2, x1:x2]
                
                if face_img.size == 0:
                    continue
                
                try:
                    gender, age = age_gender_predictor.predict(face_img)
                except:
                    gender, age = "Unknown", 0
                
                embedding = face_recognizer.get_embedding(face_img)
                
                all_faces.append({
                    "time": current_time,
                    "bbox": [x1, y1, x2, y2],
                    "gender": gender,
                    "age": age,
                    "embedding": embedding.tolist(),
                    "face_img": face_img
                })
        
        cap.release()
        
        if all_faces:
            embeddings = [face["embedding"] for face in all_faces]
            cluster_labels = face_recognizer.cluster_faces(embeddings)
            
            for i, face in enumerate(all_faces):
                face["cluster_id"] = int(cluster_labels[i])
        
        await save_results(video_id, all_faces)
        
        async with get_session() as session:
            video_record = await session.get(VideoProcessing, video_id)
            video_record.status = "completed"
            video_record.faces_count = len(all_faces)
            video_record.processing_time = time.time() - start_time
            await session.commit()
            
    except Exception as e:
        async with get_session() as session:
            video_record = await session.get(VideoProcessing, video_id)
            video_record.status = f"error: {str(e)}"
            await session.commit()
        raise e

async def save_results(video_id: str, faces_data: list):
    """Сохранение результатов в БД и файловую систему"""
    if not faces_data:
        return
    
    clusters = {}
    for face in faces_data:
        cluster_id = face["cluster_id"]
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(face)
    
    async with get_session() as session:

        for cluster_id, faces in clusters.items():

            avg_age = np.mean([f["age"] for f in faces])
            genders = [f["gender"] for f in faces]
            predominant_gender = max(set(genders), key=genders.count)

            times = [f["time"] for f in faces]
            first_seen = min(times)
            last_seen = max(times)

            face_img = faces[0]["face_img"]
            face_filename = f"static/faces/{video_id}_{cluster_id}.jpg"
            os.makedirs(os.path.dirname(face_filename), exist_ok=True)
            cv2.imwrite(face_filename, cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR))

            face_record = Face(
                video_id=video_id,
                cluster_id=cluster_id,
                avg_age=avg_age,
                predominant_gender=predominant_gender,
                first_seen=first_seen,
                last_seen=last_seen,
                thumbnail_path=f"/{face_filename}",
                embeddings=[f["embedding"] for f in faces]
            )
            
            session.add(face_record)
        
        await session.commit()