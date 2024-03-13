from fastapi import APIRouter, HTTPException
from .utils.PoeBot import SendMessage, GenerateImage
from .Schemas import BotRequest
from aiohttp import ClientSession
from pydantic import BaseModel
import asyncio
from ballyregan.models import Protocols, Anonymities
from ballyregan import ProxyFetcher

# Setting the debug mode to True, defaults to False


chat_router = APIRouter(tags=["Chat"])
proxy = ""
proxies = [
    "http://51.89.14.70:80",
    "http://52.151.210.204:9002",
    "http://38.180.36.19:80",
    "http://38.54.79.150:80",
    "https://80.91.26.137:3128",
    "http://82.223.102.92:9443",
    "http://189.240.60.166:9090",
    "https://189.240.60.168:9090",
    "http://189.240.60.171:9090",
]


class InputData(BaseModel):
    input: dict
    version: str = "727e49a643e999d602a896c774a0658ffefea21465756a6ce24b7ea4165eba6a"
    proxies: list[str] = []


async def fetch_predictions(data):
    global proxy, proxies
    proxy_set = proxy != ""
    async with ClientSession() as session:
        for p in proxies:
            if proxy_set:
                if p != proxy:
                    continue
            try:
                async with session.post(
                    "https://replicate.com/api/predictions",
                    json=data,
                    timeout=5,
                    proxy=str(p),
                ) as response:
                    if str(response.status).startswith("4"):
                        continue
                    proxy = str(p)
                    return await response.json()
            except Exception as e:
                print("Error fetching", e)
                pass
        proxy = ""


@chat_router.post("/predictions")
async def get_predictions(input_data: InputData):
    global proxies
    if input_data.proxies != []:
        proxies = input_data.proxies
    data = {
        "input": input_data.input,
        "is_training": False,
        "create_model": "0",
        "stream": False,
        "version": input_data.version,
    }
    try:
        predictions = await fetch_predictions(data)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@chat_router.post("/chat")
async def chat(req: BotRequest):
    return await SendMessage(req)


@chat_router.post("/generate_image")
async def chat(req: BotRequest):
    return await GenerateImage(req)
