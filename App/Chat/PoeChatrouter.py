from fastapi import APIRouter
from .utils.PoeBot import SendMessage
from .Schemas import BotRequest


chat_router = APIRouter(tags=["Chat"])


@chat_router.post("/chat")
async def chat(req: BotRequest):
    return await SendMessage(req)
