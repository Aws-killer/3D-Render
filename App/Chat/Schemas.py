from pydantic import BaseModel
from typing import List, Optional

class BotRequest(BaseModel):
    message: str
    bot: str
    file_upload: Optional[List[str]] = []
