import os
import uuid
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import init_db, async_session
from .models import VideoProcessing, Face  # Добавлен импорт Face

app = FastAPI(title="FaceDetector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.on_event("startup")
async def startup_event():
    await init_db()

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

@app.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks, 
    video: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    video_id = str(uuid.uuid4())
    
    file_path = f"temp_videos/{video_id}_{video.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        content = await video.read()
        buffer.write(content)

    video_record = VideoProcessing(
        id=video_id,
        file_path=file_path,
        status="uploaded"
    )
    
    db.add(video_record)
    await db.commit()

    background_tasks.add_task(process_video, video_id, file_path)
    
    return JSONResponse(
        status_code=202,
        content={
            "video_id": video_id,
            "status": "processing",
            "message": "Video is being processed"
        }
    )

@app.get("/results/{video_id}")
async def get_results(
    video_id: str, 
    db: AsyncSession = Depends(get_db)
):
    video_record = await db.get(VideoProcessing, video_id)
    if not video_record:
        raise HTTPException(status_code=404, detail="Video not found")

    result = await db.execute(select(Face).where(Face.video_id == video_id))
    faces = result.scalars().all()

    results = {
        "video_id": video_id,
        "status": video_record.status,
        "processing_time": video_record.processing_time,
        "faces_count": video_record.faces_count,
        "faces": []
    }
    
    for face in faces:
        results["faces"].append({
            "cluster_id": face.cluster_id,
            "avg_age": face.avg_age,
            "predominant_gender": face.predominant_gender,
            "first_seen": face.first_seen,
            "last_seen": face.last_seen,
            "thumbnail_path": face.thumbnail_path,
            "appearances_count": len(face.embeddings)
        })
    
    return results

@app.get("/status/{video_id}")
async def get_status(
    video_id: str, 
    db: AsyncSession = Depends(get_db)
):
    video_record = await db.get(VideoProcessing, video_id)
    if not video_record:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {
        "video_id": video_id,
        "status": video_record.status,
        "processing_time": video_record.processing_time
    }

@app.get("/")
async def root():
    return {"message": "FaceDetector API is running"}