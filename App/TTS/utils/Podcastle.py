import aiohttp
import asyncio
from App.TTS.Schemas import TTSGenerateRequest, StatusRequest
from pydantic import BaseModel


class PodcastleAPI:
    def __init__(self, username, password):
        self.base_url = "https://podcastle.ai/api"
        self.username = username
        self.password = password
        self.headers = {
            "authority": "podcastle.ai",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
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
        payload = {"username": self.username, "password": self.password}

        if not self.session:
            await self.create_session()

        async with self.session.post(url, json=payload) as response:
            response_data = await response.json()
            self.access_token = response_data["auth"]["accessToken"]
            return response_data

    async def make_request(self, tts_request: TTSGenerateRequest):
        if not self.session:
            await self.create_session()

        if not self.access_token:
            await self.signin()

        headers_with_auth = self.headers.copy()
        headers_with_auth["authorization"] = f"Bearer {self.access_token}"

        url = f"{self.base_url}/speech/text-to-speech"

        async with self.session.post(
            url, json=tts_request.dict(), headers=headers_with_auth
        ) as response:
            if response.status == 401:
                # If a 401 error is encountered, sign in again to update the access token
                await self.signin()
                # Retry the request with the updated access token
                headers_with_auth["authorization"] = f"Bearer {self.access_token}"
                async with self.session.post(
                    url, json=tts_request.dict(), headers=headers_with_auth
                ) as retry_response:
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
        headers_with_auth["authorization"] = f"Bearer {self.access_token}"

        url = f"{self.base_url}/speech/text-to-speech/{tts_status.requestId}"

        async with self.session.get(url, headers=headers_with_auth) as response:
            if response.status == 401:
                # If a 401 error is encountered, sign in again to update the access token
                await self.signin()
                # Retry the request with the updated access token
                headers_with_auth["authorization"] = f"Bearer {self.access_token}"
                async with self.session.get(
                    url, headers=headers_with_auth
                ) as retry_response:
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
