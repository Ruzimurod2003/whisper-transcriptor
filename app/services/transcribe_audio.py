import json
import os
from app.config.configuration import config
from datetime import datetime
import whisper  # Ensure this is the correct import for the Whisper model
from bson import ObjectId
from app.config.collection import audio_files, progress_statuses
from app.config.whisper_logging import write_log_error  # Use the collection from your setup


model_name = str(config.get("WHISPER_MODEL_NAME"))
download_root = "ai_model"

def transcribe_audio(audio_file):
    # Here we can take environment variables
    language = str(config.get("WHISPER_LANGUAGE"))
    verbose = bool(config.get("WHISPER_VERBOSE"))
    fp16 = bool(config.get("WHISPER_FP16"))

    model = whisper.load_model(model_name, download_root = download_root)
    # Load audio file
    audio_file_path = audio_file["path"]

    file_path = os.path.abspath(audio_file_path)

    # Transcribe audio file
    transcription = model.transcribe(
        audio=str(file_path), 
        language=language, 
        verbose=verbose, 
        fp16=fp16
    )

    return transcription["text"], json.dumps(transcription["segments"])


def update_transcription_in_db(audio_file_id, transcription, transcription_json):
    # Update the transcription in the database
    audio_files.update_one(
        {"_id": ObjectId(audio_file_id)},
        {
            "$set": 
            {
                "transcription": f"{transcription}",
                "updated_at": datetime.now(),
                "transcription_json": f"{transcription_json}"
            }
        }
    )

    # Update the transcription status in the database
    progress_statuses.update_one(
        {"file_id": str(audio_file_id)}, 
        {
            "$set": 
            {
                "status": "Transcribed"
            }
        }
    )


def process_audio_file(audio_file_id):
    try:
        # Fetch the audio file details from the database
        audio_file = audio_files.find_one({"_id": ObjectId(audio_file_id)})

        if not audio_file:
            raise ValueError("Audio file not found in database.")
        
        while True:            
            try:
                # Transcribe the audio file
                transcription, transcription_json = transcribe_audio(audio_file)

                # Update the transcription in the database
                update_transcription_in_db(audio_file_id, transcription, transcription_json)
                
                # Getting the status from the database
                progress_status = progress_statuses.find_one({"file_id": str(audio_file_id)})

                # Process continues until the status is Transcribed
                if (str(progress_status["status"]) == str("Transcribed")):
                    break
            except Exception as ex:
                write_log_error(f"Exception for {audio_file_id}, message: {ex}")

    except Exception as ex:
        write_log_error(f"Exception for {audio_file_id}, message: {ex}")
