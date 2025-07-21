from fastapi import APIRouter, UploadFile, File, BackgroundTasks
import uuid
import os
from pathlib import Path

router = APIRouter(prefix="/api", tags=["API"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_video(
        background_tasks: BackgroundTasks,
        video: UploadFile = File(...)
):
    video_id = str(uuid.uuid4())

    file_path = os.path.join(UPLOAD_DIR, f"{video_id}_{video.filename}")

    try:

        with open(file_path, "wb") as buffer:
            while content := await video.read(1024 * 1024):
                buffer.write(content)
    except Exception as e:
        return {"status": "error", "message": str(e)}

    background_tasks.add_task(process_video, file_path, video_id)

    return {
        "video_id": video_id,
        "filename": video.filename,
        "status": "processing"
    }


@router.get("/results/{video_id}")
async def get_results(video_id: str):
    return {
        "video_id": video_id,
        "status": "completed",
        "faces": [
            {"id": 1, "age": 25, "gender": "male"},
            {"id": 2, "age": 30, "gender": "female"}
        ]
    }


def process_video(file_path: str, video_id: str):
    print(f"Processing video {video_id} from {file_path}")
