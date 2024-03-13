from fastapi import APIRouter, HTTPException
from .utils.PoeBot import SendMessage, GenerateImage
from .Schemas import BotRequest
from aiohttp import ClientSession
from pydantic import BaseModel

from ballyregan.models import Protocols, Anonymities
from ballyregan import ProxyFetcher

# Setting the debug mode to True, defaults to False
fetcher = ProxyFetcher()


chat_router = APIRouter(tags=["Chat"])
proxy = ""


class InputData(BaseModel):
    input: dict
    version: str = "727e49a643e999d602a896c774a0658ffefea21465756a6ce24b7ea4165eba6a"


async def fetch_predictions(data):
    proxy_set = proxy != ""
    if not proxy_set:
        proxies = fetcher.get(
            limit=10,
            protocols=[Protocols.HTTP],
            anonymities=[Anonymities.ELITE],
        )

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
                    if response.status == 403:
                        continue
                    proxy = str(p)
                    return await response.json(), response.status
            except Exception as e:
                print(e)
                pass
        proxy = ""


async def fetch_result(id):
    url = f"https://replicate.com/api/predictions/{id}"
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(), response.status


@chat_router.post("/predictions")
async def get_predictions(input_data: InputData):
    data = {
        "input": input_data.input,
        "is_training": False,
        "create_model": "0",
        "stream": False,
        "version": input_data.version,
    }
    try:
        predictions, status_code = await fetch_predictions(data)
        return predictions, status_code
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@chat_router.post("/chat")
async def chat(req: BotRequest):
    return await SendMessage(req)


@chat_router.post("/generate_image")
async def chat(req: BotRequest):
    return await GenerateImage(req)
