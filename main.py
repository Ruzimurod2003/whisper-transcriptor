from fastapi import FastAPI, Request
from app.routes.audio_file import file_route
from app.config.configuration import config
import uvicorn

app = FastAPI(
    title="Whisper title",
    description="Whisper description",
    version="V1.0",
    docs_url="/api-doc",
    openapi_url="/api-doc/openapi.json"
)
app.include_router(file_route)


@app.get("/")
async def root(request: Request):
    client_host = request.client.host

    whisper_facts = [
        "Whisper is an automatic speech recognition (ASR) system.",
        "It is capable of transcribing and translating in Latvian language.",
        "Whisper can handle a variety of audio qualities and environments.",
        "The model is based on transformer architecture, similar to GPT models.",
        "It has been trained on a diverse dataset to improve accuracy and robustness."
    ]

    return {
        "message": "Welcome to Whisper API!",
        "client_ip": client_host,
        "whisper_facts": whisper_facts
    }


@app.get("/api/v1/status")
async def get_status():
    return {"status": "Up and running!"}


if __name__ == "__main__":
    host = config.get("APP_HOST", "0.0.0.0")
    port = int(config.get("APP_PORT", 5000))
    environment = config.get("ENVIRONMENT", "production")

    if environment == "development":
        uvicorn.run("main:app", host=host, port=port, reload=True)
    else:
        uvicorn.run(app, host=host, port=port)
