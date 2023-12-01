from poe_api_wrapper import PoeApi
from App.Chat.Schemas import BotRequest

# import pprint


client = PoeApi("sXvCnfYy8CHnXNTRlxhmVg==")
CHAT_CODE = ""


async def SendMessage(req: BotRequest):
    global CHAT_CODE
    if CHAT_CODE == "":
        for chunk in client.send_message(
            req.bot, req.message, chatCode="2rx4w5jt6zf96tn7dr1"
        ):
            pass
        CHAT_CODE = chunk["chatCode"]
    else:
        for chunk in client.send_message(req.bot, req.message, chatCode=CHAT_CODE):
            pass

    return chunk["text"]
