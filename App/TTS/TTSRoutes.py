from fastapi import APIRouter


from .Schemas import (
    StatusRequest,
    TTSGenerateRequest,
    HeyGenTTSRequest,
    DescriptRequest,
    DescriptStatusRequest,
    DescriptSfxRequest,
    DescriptTranscript,
    PiTTSRequest,
)
from .utils.Podcastle import PodcastleAPI
from .utils.HeyGen import HeygenAPI
from .utils.Pi import PiAIClient
from .utils.Descript import DescriptTTS
import os
import asyncio

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
import os

tts_router = APIRouter(tags=["TTS"])
data = {"username": os.environ.get("USERNAME"), "password": os.environ.get("PASSWORD")}
tts = PodcastleAPI(**data)
data = {
    "account": os.environ.get("HEYGEN_USERNAME"),
    "password": os.environ.get("HEYGEN_PASSWORD"),
    "token": os.environ.get("HEYGEN_TOKEN"),
}

descript_tts = DescriptTTS()
heyGentts = HeygenAPI(**data)
pi = PiAIClient()


@tts_router.post("/generate_tts")
async def generate_voice(req: TTSGenerateRequest):
    print("here --entered!")
    return await tts.make_request(req)


@tts_router.post("/heygen_tts")
async def generate_heygen_voice(req: HeyGenTTSRequest):
    print("hey gen here")
    return await heyGentts.tts_request(req)


@tts_router.post("/descript_tts")
async def generate_descript_voice(req: DescriptRequest):
    return await descript_tts.overdub_text(**req.__dict__)


@tts_router.post("/descript_status")
async def status_descript(req: DescriptStatusRequest):
    return await descript_tts.request_status(req.id)


@tts_router.post("/descript_music")
async def descript_music(req: DescriptSfxRequest):
    return await descript_tts.search_music(req.query)


@tts_router.post("/descript_sfx")
async def descript_sfx(req: DescriptSfxRequest):
    return await descript_tts.search_sound_effects(req.query)


@tts_router.post("/descript_transcript")
async def descript_transcript(req: DescriptTranscript):
    return await descript_tts.get_transcription(req)
    # return await descript_tts.search_sound_effects(req.query)


@tts_router.post("/descript_unsplash")
async def descript_unsplash(req: DescriptSfxRequest):
    return await descript_tts.search_unsplash_images(req.query)


@tts_router.get("/descript_voices")
async def voices_descript():
    return await descript_tts.get_voices()


@tts_router.get("/descript_auto_refresh")
async def auto_refresh():
    asyncio.create_task(descript_tts.start_token_refresh_schedule())
    return {"message": "Token refresh schedule started in the background."}


@tts_router.post("/status")
async def search_id(req: StatusRequest):
    return await tts.check_status(req)


@tts_router.post("/pi_tts")
async def pi_tts(req: PiTTSRequest):
    return await pi.say(text=req.text, voice=req.voice)


@tts_router.get("/audio/{audio_name}")
async def serve_audio(request: Request, audio_name: str):
    audio_directory = "/tmp/Audio"
    audio_path = os.path.join(audio_directory, audio_name)
    if not os.path.isfile(audio_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    range_header = request.headers.get("Range", None)
    audio_size = os.path.getsize(audio_path)

    if range_header:
        start, end = range_header.strip().split("=")[1].split("-")
        start = int(start)
        end = audio_size if end == "" else int(end)

        headers = {
            "Content-Range": f"bytes {start}-{end}/{audio_size}",
            "Accept-Ranges": "bytes",
            # Optionally, you might want to force download by uncommenting the next line:
            # "Content-Disposition": f"attachment; filename={audio_name}",
        }

        content = read_file_range(audio_path, start, end)
        return StreamingResponse(content, media_type="audio/mpeg", headers=headers)

    return FileResponse(audio_path, media_type="audio/mpeg")


def read_file_range(path, start, end):
    """Helper function to read specific range of bytes from a file."""
    with open(path, "rb") as file:
        file.seek(start)
        # Be sure to handle the case where `end` is not the last byte
        return file.read(end - start + 1)
