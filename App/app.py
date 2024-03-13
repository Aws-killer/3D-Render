from fastapi import FastAPI

from fastapi.middleware.gzip import GZipMiddleware

from .TTS.TTSRoutes import tts_router
# from .Embedding.EmbeddingRoutes import embeddigs_router
# from .Chat.PoeChatrouter import chat_router

from fastapi.middleware.cors import CORSMiddleware

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

import logging


# Configure logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )


app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())


@app.get("/")
async def landing_page():
    return {"code": 200, "message": "we are back!"}


# app.include_router(embeddigs_router)
app.include_router(tts_router)
# app.include_router(chat_router)
