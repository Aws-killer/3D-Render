import aiohttp



from pydantic import BaseModel, Field, validator
from typing import List, Optional
import uuid
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


class HeygenAPI:
    def __init__(self, account, password, token):
        self.base_url = "https://api2.heygen.com/v1"
        self.account = account
        self.password = password
        self.token = token
        self.session = None
        self.session_token = None

    async def create_session(self):
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def login(self):
        url = f"{self.base_url}/pacific/login"
        payload = {
            "login_type": "email",
            "account": self.account,
            "password": self.password,
            "token": self.token,
        }

        if not self.session:
            await self.create_session()

        async with self.session.post(url, json=payload) as response:
            response_data = await response.json()
            self.session_token = response_data.get("data", {}).get("session_token")
            return response_data

    async def relogin(self):
        # Function to relogin and update the session token
        login_result = await self.login()
        if login_result.get("code") == 100:
            self.session_token = login_result["data"]["session_token"]
            return True
        return False

    async def tts_request(self, req: HeyGenTTSRequest):
        if not self.session_token or not self.session_token:
            await self.login()

        url = f"{self.base_url}/online/text_to_speech.generate"
        headers = {
            "content-type": "application/json",
            "x-session-token": self.session_token,
        }

        tts_payload = {
            "text_type": "ssml",
            "output_format": "wav",
            "text": req.text,
            "voice_id": req.voice_id,
            "settings": {},
        }

        async with self.session.post(
            url, json=tts_payload, headers=headers
        ) as response:
            if response.status == 401:
                # If a 401 error is encountered, relogin and retry the request
                if await self.relogin():
                    headers["x-session-token"] = self.session_token
                    response = await self.session.post(
                        url, json=tts_payload, headers=headers
                    )

            response_data = await response.json()
            return response_data

    async def __aenter__(self):
        if not self.session:
            await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close_session()


async def main():
    data = {
        "account": "mebaxo5916@tospage.com",
        "password": "HBBHN4RPs_rA$%R",
        "token":'+DTX2g=='
    }
    async with HeygenAPI(**data) as heygen:
        req = HeyGenTTSRequest(
            text="Hello, this is a test",
            # voice_id="1",
        )
        response = await heygen.tts_request(req)
        print(response)

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())