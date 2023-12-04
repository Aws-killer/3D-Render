from fastapi import APIRouter
from .utils.PoeBot import SendMessage, GenerateImage
from .Schemas import BotRequest


chat_router = APIRouter(tags=["Chat"])


@chat_router.post("/chat")
async def chat(req: BotRequest):
    return await SendMessage(req)


@chat_router.post("/generate_image")
async def chat(req: BotRequest):
    return await GenerateImage(req)
