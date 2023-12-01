from pydantic import BaseModel


class BotRequest(BaseModel):
    message: str
    bot: str
