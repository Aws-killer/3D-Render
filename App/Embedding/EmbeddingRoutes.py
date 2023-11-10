from fastapi import APIRouter, BackgroundTasks

from .utils.Initialize import TextSearch, IdSearch, LookUpIds
from .Schemas import SearchRequest, AddDocumentRequest, TrendingRequest
import redis, os, json

REDIS = os.environ.get("REDIS")
cache = redis.from_url(REDIS)


embeddigs_router = APIRouter(tags=["embeddings"])


# create
@embeddigs_router.post("/add_document")
async def create_embeddings(req: AddDocumentRequest):
    pass


@embeddigs_router.get("/Trending")
async def getTrending(req: TrendingRequest):
    LookUpIds(req.imdb_ids)


@embeddigs_router.post("/search_id")
async def search_id(
    req: SearchRequest,
    background_tasks: BackgroundTasks,
):
    data = cache.get(f"recommendations:{req.query}")
    if data is not None:
        return json.loads(data)

    data = IdSearch(query=req.query, background_task=background_tasks)
    cache.set(f"recommendations:{req.query}", json.dumps(data), ex=72000)
    return data


@embeddigs_router.post("/search_text")
async def search_text(reqx: SearchRequest):
    return TextSearch(query=reqx.query)
