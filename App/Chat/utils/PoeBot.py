from poe_api_wrapper import PoeApi
from App.Chat.Schemas import BotRequest

# import pprint


client = PoeApi("sXvCnfYy8CHnXNTRlxhmVg==")
CHAT_CODE = ""
print(client.get_chat_history()["data"])


async def SendMessage(req: BotRequest):
    global CHAT_CODE, client
    counter = 0
    while True:
        try:
            if CHAT_CODE == "":
                for chunk in client.send_message(
                    req.bot, req.message, chatCode="2rx4w5jt6zf96tn7dr1"
                ):
                    pass
                CHAT_CODE = chunk["chatCode"]
            else:
                for chunk in client.send_message(
                    req.bot, req.message, chatCode=CHAT_CODE
                ):
                    pass

            return {"response": chunk["text"], "code": 200}
        except:
            if counter > 4:
                return {"response": "Try again later", "code": 500}
            client = PoeApi("sXvCnfYy8CHnXNTRlxhmVg==")
            CHAT_CODE = ""
            counter += 1
            print(client.get_chat_history()["data"])
