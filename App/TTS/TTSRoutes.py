from fastapi import APIRouter


from .Schemas import StatusRequest, TTSGenerateRequest, HeyGenTTSRequest
from .utils.Podcastle import PodcastleAPI
from .utils.HeyGen import HeygenAPI
import os

tts_router = APIRouter(tags=["TTS"])
data = {"username": os.environ.get("USERNAME"), "password": os.environ.get("PASSWORD")}
tts = PodcastleAPI(**data)
data = {
    "account": os.environ.get("HEYGEN_USERNAME"),
    "password": os.environ.get("HEYGEN_PASSWORD"),
}
heyGentts = HeygenAPI(**data)


@tts_router.post("/generate_tts")
async def generate_voice(req: TTSGenerateRequest):
    print("here --entered!")
    return await tts.make_request(req)


@tts_router.post("/heygen_tts")
async def generate_heygen_voice(req: HeyGenTTSRequest):
    print("hey gen here")
    return await heyGentts.tts_request(req)


@tts_router.post("/status")
async def search_id(req: StatusRequest):
    return await tts.check_status(req)
