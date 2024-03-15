from fastapi import APIRouter


from .Schemas import (
    StatusRequest,
    TTSGenerateRequest,
    HeyGenTTSRequest,
    DescriptRequest,
    DescriptStatusRequest,
    DescriptSfxRequest,
)
from .utils.Podcastle import PodcastleAPI
from .utils.HeyGen import HeygenAPI
from .utils.Descript import DescriptTTS
import os
import asyncio

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


@tts_router.post("/descript_sfx")
async def descript_sfx(req: DescriptSfxRequest):
    return await descript_tts.search_sound_effects(req.query)


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
