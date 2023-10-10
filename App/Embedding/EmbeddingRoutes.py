from fastapi import APIRouter, BackgroundTasks

from .utils.Initialize import TextSearch, IdSearch
from .Schemas import SearchRequest, AddDocumentRequest

embeddigs_router = APIRouter(tags=["embeddings"])


# create
@embeddigs_router.post("/add_document")
async def create_embeddings(req: AddDocumentRequest):
    pass


@embeddigs_router.post("/search_id")
async def search_id(
    req: SearchRequest,
    background_tasks: BackgroundTasks,
):
    return IdSearch(query=req.query, background_task=background_tasks)


@embeddigs_router.post("/search_text")
async def search_text(req: SearchRequest):
    return TextSearch(query=req.query)
