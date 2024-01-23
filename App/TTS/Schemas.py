from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uuid


class Speak(BaseModel):
    paragraphId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    speaker: str
    text: str
    voiceId: str = Field(
        default="c60166365edf46589657770d", alias="speaker"
    )  # Default speaker value

    def __init__(self, **data):
        data["text"] = (
            data.get("text")
            if "<speak>" in data.get("text")
            else f"<speak>{data.get('text')}</speak>"
        )
        super().__init__(**data)

class DescriptSfxRequest(BaseModel):
    query:str

class DescriptRequest(BaseModel):
    text: str
    speaker: Optional[str]=Field(default="Lawrance")
    _voice_id: Optional[str] 

class DescriptStatusRequest(BaseModel):
    id:str




class HeyGenTTSRequest(BaseModel):
    voice_id: str = Field(default="d7bbcdd6964c47bdaae26decade4a933")
    rate: str = Field(default="1")
    pitch: str = Field(default="-3%")
    text: str = "Sample"

    @validator("text")
    def validate_age(cls, value, values):
        if not "speak" in value:
            return f'<speak> <voice name="{values.get("voice_id")}"><prosody rate="{values.get("rate")}" pitch="{values.get("pitch")}">{value}</prosody></voice></speak>'
        else:
            return value


class TTSGenerateRequest(BaseModel):
    paragraphs: List[Speak]
    requestId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspaceId: str = Field(default_factory=lambda: str(uuid.uuid4()))


class StatusRequest(BaseModel):
    requestId: str


class GetTranscriptions(BaseModel):
    userId: int
