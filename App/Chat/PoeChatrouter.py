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
proxies = []


class InputData(BaseModel):
    input: dict
    version: str = "727e49a643e999d602a896c774a0658ffefea21465756a6ce24b7ea4165eba6a"
    proxies: list[str] = []
    is_proxied: bool = False


async def fetch_predictions(data, is_proxied=False):
    global proxy, proxies
    if is_proxied:
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
                    ) as response:
                        if str(response.status).startswith("4"):
                            continue
                        proxy = str(p)
                        temp = await response.json()
                        print(temp)
                        return temp
                except Exception as e:
                    print("Error fetching", e)
                    pass
            proxy = ""
    else:
        try:
            async with session.post(
                "https://replicate.com/api/predictions",
                json=data,
                timeout=5,
            ) as response:
                temp = await response.json()
                return temp
        except Exception as e:
            print("Error fetching", e)
            pass


@chat_router.post("/predictions")
async def get_predictions(input_data: InputData):
    global proxies
    if input_data.proxies != []:
        proxies = input_data.proxies
    else:

        proxies = [
            "http://51.89.14.70:80",
            "http://52.151.210.204:9002",
            "http://38.180.36.19:80",
        ]
    data = {
        "input": input_data.input,
        "is_training": False,
        "create_model": "0",
        "stream": False,
        "version": input_data.version,
    }
    try:
        predictions = await fetch_predictions(data, input_data.is_proxied)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@chat_router.post("/chat")
async def chat(req: BotRequest):
    return await SendMessage(req)


@chat_router.post("/generate_image")
async def chat(req: BotRequest):
    return await GenerateImage(req)
