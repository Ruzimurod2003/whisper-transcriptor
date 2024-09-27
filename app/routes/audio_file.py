import shutil
import os
import uuid
from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.security import APIKeyHeader
from app.config.whisper_logging import write_log_error
from app.models.audio_file import AudioFile
from app.config.collection import audio_files, progress_statuses
from app.models.progress_status import ProgressStatus
from app.rabbitmq.producer import send_message
from app.config.configuration import config
from app.schemas.audio_file import serialize_dict, serialize_list

file_route = APIRouter()

# Define the base upload directory
BASE_UPLOAD_DIRECTORY = os.path.join("storage")

# Define the upload directory structure based on the current date
date = datetime.now()
UPLOAD_DIRECTORY = os.path.join(
    BASE_UPLOAD_DIRECTORY, str(date.year), str(date.month), str(date.day)
)

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Get the absolute path of the upload directory
full_path = os.path.abspath(UPLOAD_DIRECTORY)

# Define allowed audio file extensions
AUDIO_EXTENSIONS = {
    'wav', 'mp3', 'aac', 'flac', 'alac',
    'ogg', 'wma', 'aiff', 'm4a', 'm4b',
    'm4p', 'mid', 'midi', 'mpc', 'opus'
}


def is_audio_file(filename: str) -> bool:
    """Check if the file has a valid audio extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in AUDIO_EXTENSIONS


x_key_header = APIKeyHeader(name="x-key", auto_error=False)
X_KEY = str(config.get("SECRET_TOKEN"))


def get_x_token(key_header: str = Depends(x_key_header)):
    if key_header is None or key_header != X_KEY:
        raise HTTPException(status_code=401)
    return key_header


@file_route.post(
    path="/api/v1/upload-audio-file",
    tags=["Whisper tag"],
    response_description="This endpoint for upload file",
    summary="This endpoint for upload file for manually"
)
async def upload_audio_file(
        uploaded_file: UploadFile = File(...),
        x_token: str = Depends(get_x_token)
):
    if not is_audio_file(uploaded_file.filename):
        raise HTTPException(status_code=400, detail="You need to upload an audio file")

    file_extension = uploaded_file.filename.rsplit(".", 1)[1].lower()
    new_filename = f"{uuid.uuid4()}.{file_extension}"
    file_location = os.path.join(UPLOAD_DIRECTORY, new_filename)

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)
    except Exception as e:
        write_log_error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    audio_file = AudioFile(
        file_name=new_filename,
        path=file_location,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    try:
        audio_files.insert_one(audio_file.model_dump())
        audio_file_id = str(audio_files.find_one({"file_name": new_filename})["_id"])

        progress_status = ProgressStatus(
            file_id=audio_file_id,
            status="Uploaded"
        )
        progress_statuses.insert_one(progress_status.model_dump())

    except Exception as e:
        write_log_error(f"Error saving file to database: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error saving file to database: {e}"
        )

    try:
        send_message(audio_file_id)
        progress_statuses.update_one(
            {"file_id": audio_file_id}, 
            {"$set": {"status": "Queued"}}
        )
    except Exception as e:
        write_log_error(f"Error queuing file to RabbitMQ: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error queuing file to RabbitMQ: {e}"
        )

    return {
        "new_filename": new_filename,
        "id": audio_file_id,
        "status": "Queued"
    }


@file_route.get(
    path="/api/v1/file-status",
    tags=["Whisper tag"],
    response_description="This endpoint for check status file",
    summary="This endpoint for check status file for manually"
)
async def get_file_status(
        file_id: str,
        x_token: str = Depends(get_x_token)
):
    progress_status = progress_statuses.find_one({"file_id": file_id})

    if progress_status is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Not found status of thi: {file_id}"
        )
    return {
        "file_id": file_id,
        "status": progress_status["status"]
    }


@file_route.get(
    path="/api/v1/files-by-id",
    tags=["Whisper tag"],
    response_description="This endpoint for get file by id",
    summary="This endpoint for get file by id for manually"
)
async def get_file_by_id(
    file_id: str,
    x_token: str = Depends(get_x_token)
):
    file = audio_files.find_one({"_id": ObjectId(file_id)})

    if file is None:
        raise HTTPException(status_code=404, detail=f"Not found")
    return serialize_dict(file)


@file_route.get(
    path="/api/v1/files",
    tags=["Whisper tag"],
    response_description="This endpoint for get all files",
    summary="This endpoint for get all files for manually"
)
async def get_files(
        x_token: str = Depends(get_x_token)
):
    files = audio_files.find()

    if files is None:
        raise HTTPException(status_code=404, detail=f"Not found")
    return serialize_list(files)
