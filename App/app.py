from fastapi import FastAPI

from fastapi.middleware.gzip import GZipMiddleware


from .Embedding.EmbeddingRoutes import embeddigs_router


from fastapi.middleware.cors import CORSMiddleware


import logging


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


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


@app.get("/")
async def landing_page():
    return {"code": 200, "message": "we are back!"}


app.include_router(embeddigs_router)
