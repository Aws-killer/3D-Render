from typing import List, Optional
from pydantic import EmailStr, BaseModel
from datetime import date, datetime, time, timedelta


class BaseRequest(BaseModel):
    user: Optional[int]
    id: Optional[int]
    content: Optional[str]


class editRequest(BaseRequest):
    updatedAt: datetime = datetime.now()
