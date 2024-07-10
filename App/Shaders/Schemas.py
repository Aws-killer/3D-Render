from typing import List, Optional
from pydantic import EmailStr, BaseModel
from datetime import date, datetime, time, timedelta


class BaseRequest(BaseModel):
    image: str


class BaseResponse(BaseModel):
    result: str
