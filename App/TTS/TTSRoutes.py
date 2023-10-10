from fastapi import APIRouter


from .Schemas import StatusRequest, TTSGenerateRequest
from .utils.Podcastle import PodcastleAPI
import os

tts_router = APIRouter(tags=["TTS"])
data = {"username": os.environ.get("USERNAME"), "password": os.environ.get("PASSWORD")}
tts = PodcastleAPI(**data)


#
@tts_router.post("/generate_tts")
async def generate_voice(req: TTSGenerateRequest):
    print("here --entered!")
    return await tts.make_request(req)


@tts_router.post("/status")
async def search_id(req: StatusRequest):
    return await tts.check_status(req)


# @tts_router.post("/search_text")
# async def search_text(req: SearchRequest):
#     return TextSearch(query=req.query)
