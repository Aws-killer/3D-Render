import aiohttp
import asyncio
from App.TTS.Schemas import TTSGenerateRequest,StatusRequest
from pydantic import BaseModel

class PodcastleAPI:
    def __init__(self, username, password):
        self.base_url = "https://podcastle.ai/api"
        self.username = username
        self.password = password
        self.headers = {
            'authority': 'podcastle.ai',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            # Add your other headers here
        }
        self.session = None  # Initialize the session in the constructor
        self.access_token = None

    async def create_session(self):
        self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def signin(self):
        url = f"{self.base_url}/auth/signin"
        payload = {
            "username": self.username,
            "password": self.password
        }

        if not self.session:
            await self.create_session()

        async with self.session.post(url, json=payload) as response:
            response_data = await response.json()
            self.access_token = response_data['auth']['accessToken']
            return response_data

    async def make_request(self, tts_request: TTSGenerateRequest):
        if not self.session:
            await self.create_session()

        if not self.access_token:
            await self.signin()

        headers_with_auth = self.headers.copy()
        headers_with_auth['authorization'] = f"Bearer {self.access_token}"

        url = f"{self.base_url}/speech/text-to-speech"

        async with self.session.post(url, json=tts_request.dict(), headers=headers_with_auth) as response:
            if response.status == 401:
                # If a 401 error is encountered, sign in again to update the access token
                await self.signin()
                # Retry the request with the updated access token
                headers_with_auth['authorization'] = f"Bearer {self.access_token}"
                async with self.session.post(url, json=tts_request.dict(), headers=headers_with_auth) as retry_response:
                    response_text = await retry_response.json()
                    return response_text
            else:
                response_text = await response.json()
                return response_text

    async def check_status(self, tts_status: StatusRequest):
        if not self.session:
            await self.create_session()

        if not self.access_token:
            await self.signin()

        headers_with_auth = self.headers.copy()
        headers_with_auth['authorization'] = f"Bearer {self.access_token}"

        url = f"{self.base_url}/speech/text-to-speech/{tts_status.requestId}"

        async with self.session.get(url, headers=headers_with_auth) as response:
            if response.status == 401:
                # If a 401 error is encountered, sign in again to update the access token
                await self.signin()
                # Retry the request with the updated access token
                headers_with_auth['authorization'] = f"Bearer {self.access_token}"
                async with self.session.get(url, headers=headers_with_auth) as retry_response:
                    response_text = await retry_response.json()
                    return response_text
            else:
                response_text = await response.json()
                return response_text




    async def __aenter__(self):
        if not self.session:
            await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close_session()

# Example usage:
if __name__ == "__main__":
    class Speak(BaseModel):
        paragraphId: str
        text: str
        speaker: str

    class TTSGenerateRequest(BaseModel):
        paragraphs: [Speak]
        requestId: str
        workspaceId: str

    async def main():
        username = "veyivib549@gronasu.com"
        password = "k7bNvgmJUda3yEG"

        # Create a TTSGenerateRequest object
        tts_request = TTSGenerateRequest(
            paragraphs=[
                Speak(
                    paragraphId="6f05p",
                    text="<speak>Hey Daniel. Are you ok?. Manchester United almost lost yesterday  </speak>",
                    speaker="c60166365edf46589657770d"
                )
            ],
            requestId="7d6018ae-9617-4d22-879f-5e67283fa140",
            workspaceId="f84fd58e-2899-4531-9f51-77c155c1e294"
        )

        async with PodcastleAPI(username, password) as podcastle_api:
            # Make the TTS request using the TTSGenerateRequest object
            response_text = await podcastle_api.make_request(tts_request)
            print(response_text)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
