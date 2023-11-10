from pydantic import BaseModel


class AddDocumentRequest(BaseModel):
    content: str
    metadata: dict


class SearchRequest(BaseModel):
    query: str


class TrendingRequest(BaseModel):
    imdb_ids: list[str]


class GetTranscriptions(BaseModel):
    userId: int
