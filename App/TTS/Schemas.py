from pydantic import BaseModel,Field
from typing import List,Optional
import uuid

class Speak(BaseModel):
    paragraphId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    speaker: str
    text: str
    voiceId: str = Field(default="c60166365edf46589657770d", alias="speaker") # Default speaker value

    def __init__(self, **data):
        data["text"] = data.get('text') if  '<speak>' in data.get('text') else f"<speak>{data.get('text')}</speak>"
        super().__init__(**data)



class TTSGenerateRequest(BaseModel):
    paragraphs: List[Speak]
    requestId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str =Field(default_factory=lambda: str(uuid.uuid4()))


class StatusRequest(BaseModel):
    requestId: str


class GetTranscriptions(BaseModel):
    userId: int
