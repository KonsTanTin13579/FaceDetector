import torch
import numpy as np
from facenet_pytorch import InceptionResnetV1
from sklearn.cluster import DBSCAN

class FaceRecognizer:
    def __init__(self, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
        self.clusterer = DBSCAN(eps=0.6, min_samples=2, metric='euclidean')
        
    def get_embedding(self, face_image):
        """Получение эмбеддинга лица"""
        if not isinstance(face_image, torch.Tensor):
            face_tensor = torch.tensor(face_image / 255.0).permute(2, 0, 1).unsqueeze(0).float()
        face_tensor = face_tensor.to(self.device)
        
        with torch.no_grad():
            embedding = self.model(face_tensor).cpu().numpy()
        
        return embedding.flatten()
    
    def cluster_faces(self, embeddings):
        """Кластеризация лиц"""
        if len(embeddings) == 0:
            return []
            
        embeddings_array = np.vstack(embeddings)
        labels = self.clusterer.fit_predict(embeddings_array)
        return labels