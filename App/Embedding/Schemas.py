from pydantic import BaseModel


class AddDocumentRequest(BaseModel):
    content: str
    metadata: dict


class SearchRequest(BaseModel):
    query: str


class GetTranscriptions(BaseModel):
    userId: int
