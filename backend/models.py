from sqlalchemy import Column, String, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class VideoProcessing(Base):
    __tablename__ = "videos"
    
    id = Column(String, primary_key=True)
    file_path = Column(String)
    status = Column(String)
    faces_count = Column(Integer, default=0)
    processing_time = Column(Float, default=0.0)

class Face(Base):
    __tablename__ = "faces"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String)
    cluster_id = Column(Integer)
    avg_age = Column(Float)
    predominant_gender = Column(String)
    first_seen = Column(Float)
    last_seen = Column(Float)
    thumbnail_path = Column(String)
    embeddings = Column(JSON)