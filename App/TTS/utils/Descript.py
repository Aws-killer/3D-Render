import aiohttp
import asyncio, wave
import json, pprint, uuid, os, datetime
import tempfile, shutil
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, HttpUrl
from App.TTS.Schemas import DescriptTranscript
from pydub import AudioSegment


class Metadata(BaseModel):
    filename: str
    type: str


class Artifact(BaseModel):
    asset_id: str
    created_at: datetime
    file_extension: str
    id: str
    is_segmented: bool
    lookup_key: HttpUrl
    md5: str
    metadata: Metadata
    read_url: HttpUrl
    size: int
    status: str
    uploaded_by: str


class TTSResponse(BaseModel):
    artifacts: List[Artifact]
    created_at: datetime
    created_by: str
    id: str
    lookup_key: HttpUrl
    metadata: Optional[dict]


class DescriptTTS:
    def __init__(self, refresh_token=None):
        self.client_id = "VDfu7rg4pdCELWsrQjcw2tG63a8Qlymi"
        self.refresh_token_url = "https://auth0.descript.com/oauth/token"
        self.project_id = "f734c6d7-e39d-4c1d-8f41-417f94cd37ce"
        self.bearer_token = None
        self.voice_ids = {
            "Henry": "569fffb0-05a3-48a2-96a3-bf411c376477",
            "Malcom": "75f8b86e-d05d-4862-a228-8d96fdf55258",
            "Lawrance": "042460c0-98a5-41ae-9f31-33672ebb9016",
            ## de
        }

        self.refresh_token = refresh_token
        self.tau_id = "90f9e0ad-594e-4203-9297-d4c7cc691e5x"

    def concatenate_wave_files(self, input_file_paths):
        """
        Concatenates multiple wave files and saves the result to a new file.

        :param input_file_paths: A list of paths to the input wave files.
        """
        temp_dir = tempfile.mkdtemp()
        # Generate a unique random filename
        random_filename = str(uuid.uuid4()) + ".wav"
        output_file_path = os.path.join(temp_dir, random_filename)

        # Check if input file paths are provided
        if not input_file_paths:
            raise ValueError("No input file paths provided.")

        # Validate output file path
        if not output_file_path:
            raise ValueError("Output file path is empty.")

        # Validate input file paths
        for input_file_path in input_file_paths:
            if not input_file_path:
                raise ValueError("Empty input file path found.")

        # Validate and get parameters from the first input file
        with wave.open(input_file_paths[0], "rb") as input_file:
            n_channels = input_file.getnchannels()
            sampwidth = input_file.getsampwidth()
            framerate = input_file.getframerate()
            comptype = input_file.getcomptype()
            compname = input_file.getcompname()

        # Open the output file for writing
        output_file = wave.open(output_file_path, "wb")
        output_file.setnchannels(n_channels)
        output_file.setsampwidth(sampwidth)
        output_file.setframerate(framerate)
        output_file.setcomptype(comptype, compname)

        # Concatenate and write data from all input files to the output file
        for input_file_path in input_file_paths:
            with wave.open(input_file_path, "rb") as input_file:
                output_file.writeframes(input_file.readframes(input_file.getnframes()))

        # Close the output file
        output_file.close()

        return output_file_path

    async def login_and_get_bearer_token(self):
        # Step 1: Use refresh token to get a new access token
        new_bearer_token, new_refresh_token = await self.refresh_access_token()

        # Step 2: Update the new refresh token to the Firebase Realtime Database
        await self.update_refresh_token(new_refresh_token)

        # Step 3: Set the new bearer token for further use
        self.bearer_token = new_bearer_token
        self.refresh_token = new_refresh_token

    async def refresh_access_token(self):
        # Load the existing refresh token from Firebase
        if self.refresh_token == None:
            await self.load_existing_refresh_token()

        # Prepare the payload for token refresh
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
        }

        # Request a new access token using the refresh token
        async with aiohttp.ClientSession() as session:
            async with session.post(self.refresh_token_url, data=payload) as response:
                if response.status == 200:
                    # Parse the response to get the new access token and refresh token
                    response_data = await response.json()
                    new_bearer_token = response_data.get("access_token")
                    new_refresh_token = response_data.get("refresh_token")

                    return new_bearer_token, new_refresh_token
                else:
                    raise Exception(
                        f"Failed to refresh access token. Status code: {response.status}, Error: {await response.text()}"
                    )

    async def load_existing_refresh_token(self):
        # Load the existing refresh token from Firebase
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://herokuserver-185316.firebaseio.com/refresh_token_descript.json"
            ) as response:
                if response.status == 200:
                    # Parse the response to get the existing refresh token
                    data = await response.json()
                    self.refresh_token = data.get("refresh_token")
                else:
                    raise Exception(
                        f"Failed to load existing refresh token. Status code: {response.status}, Error: {await response.text()}"
                    )

    async def download_and_store_file(self, access_url):
        temp_dir = tempfile.mkdtemp()
        # Generate a unique random filename
        random_filename = str(uuid.uuid4()) + ".wav"
        file_path = os.path.join(temp_dir, random_filename)

        async with aiohttp.ClientSession() as session:
            async with session.get(access_url) as response:
                if response.status == 200:
                    with open(file_path, "wb") as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)

        # Schedule the file for deletion after 10 minutes
        delete_time = datetime.now() + timedelta(minutes=10)

        async def schedule_delete():
            while datetime.now() < delete_time:
                await asyncio.sleep(60)  # Check every minute
            shutil.rmtree(
                temp_dir, ignore_errors=True
            )  # Delete the temporary directory

            asyncio.ensure_future(schedule_delete())

        return file_path

    def calculate_audio_duration(self, audio_file):
        wav_file = AudioSegment.from_file(audio_file, format="wav")
        duration_in_seconds = str(float(len(wav_file) / 1000))
        return duration_in_seconds

    async def search_unsplash_images(self, query_terms):
        url = "https://api.descript.com/v2/cloud_libraries/providers/unsplash/image/search"
        data = {
            "tracking_info": {"project_id": self.project_id},
            "pagination_info": {"page": 2, "page_size": 25},
            "query": {"terms": query_terms},
        }

        try:
            response = await self.make_authenticated_request(
                url, method="POST", data=data
            )
            return response
        except Exception as e:
            print(f"Failed to search Unsplash images: {e}")
            return None

    async def search_music(self, query_terms):
        url = "https://web.descript.com/v2/cloud_libraries/providers/stock-music/audio/search"
        data = {
            "tracking_info": {"project_id": self.project_id},
            "pagination_info": {"page": 2, "page_size": 25},
            "query": {"terms": query_terms},
        }

        try:
            response = await self.make_authenticated_request(
                url, method="POST", data=data
            )
            return response
        except Exception as e:
            print(f"Failed to search music: {e}")
            return None

    async def search_sound_effects(self, query_terms):
        url = "https://api.descript.com/v2/cloud_libraries/providers/stock-sfx/audio/search"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "authorization": f"Bearer {self.bearer_token}",  # Use the valid bearer token
        }
        data = {
            "tracking_info": {"project_id": self.project_id},
            "pagination_info": {"page": 1, "page_size": 25},
            "query": {"terms": query_terms},
        }

        try:
            response = await self.make_authenticated_request(
                url, method="POST", data=data
            )
            return response
        except Exception as e:
            print(f"Failed to search sound effects: {e}")
            return {"status": str(e)}

    async def get_voices(self):
        url = "https://api.descript.com/v2/users/me/voices"
        try:
            response = await self.make_authenticated_request(url)
            voices = response
            self.voice_ids = {voice["name"]: voice["id"] for voice in voices}

            return voices
        except Exception as e:
            print(f"Failed to fetch voices: {e}")
            return None

    async def start_token_refresh_schedule(self):
        while True:
            try:
                new_bearer_token, new_refresh_token = await self.refresh_access_token()
                self.bearer_token = new_bearer_token
                self.refresh_token = new_refresh_token

                # Step 2: Update the new refresh token to the Firebase Realtime Database
                await self.update_refresh_token(new_refresh_token)

                print("Token refreshed successfully")
            except Exception as e:
                print(f"Failed to refresh token: {e}")

            # Wait for 24 hours before the next refresh
            await asyncio.sleep(24 * 60 * 60)

    async def update_refresh_token(self, new_refresh_token):
        # Update the new refresh token to Firebase
        data = {"refresh_token": new_refresh_token}
        async with aiohttp.ClientSession() as session:
            async with session.put(
                "https://herokuserver-185316.firebaseio.com/refresh_token_descript.json",
                json=data,
            ) as response:
                if response.status != 200:
                    raise Exception(
                        f"Failed to update refresh token. Status code: {response.status}, Error: {await response.text()}"
                    )

    async def make_request_with_retry(self, session, method, url, headers, data):
        if type(data) == dict:
            args = {"json": data}
        else:
            args = {"data": data}
        # print(**args)
        async with session.request(method, url, headers=headers, **args) as response:
            if response.status < 300:
                return await response.json()
            elif response.status == 401:
                raise aiohttp.ClientResponseError(
                    response.request_info, response.history, status=response.status
                )
            else:
                raise aiohttp.ClientResponseError(
                    response.request_info, response.history, status=response.status
                )

    async def make_authenticated_request(
        self,
        url,
        method="GET",
        data=None,
    ):
        if not self.bearer_token:
            await self.login_and_get_bearer_token()  # Make sure we have a valid bearer token

        headers = {
            "authority": "api.descript.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "accept-version": "v1",
            "authorization": f"Bearer {self.bearer_token}",
            "cache-control": "no-cache",
            "origin": "https://web.descript.com",
            "pragma": "no-cache",
            "referer": "https://web.descript.com/",
            "sec-ch-ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "x-descript-app-build-number": "20231206.146",
            "x-descript-app-build-type": "release",
            "x-descript-app-id": "48db7358-5ebc-4866-b672-10b412ac39c1",
            "x-descript-app-name": "web",
            "x-descript-app-version": "78.2.4",
            "x-descript-auth": "auth0",
        }

        async with aiohttp.ClientSession() as session:
            try:
                return await self.make_request_with_retry(
                    session, method, url, headers, data
                )
            except aiohttp.ClientResponseError as e:
                if e.status == 401:
                    self.refresh_token = None
                    await self.login_and_get_bearer_token()
                    headers["authorization"] = f"Bearer {self.bearer_token}"
                    return await self.make_request_with_retry(
                        session, method, url, headers, data
                    )
                else:
                    raise e

    async def get_transcription(self, query: DescriptTranscript):
        data = aiohttp.FormData()
        audio_paths = []
        audio_path = ""
        for url in query.audio_url:
            temp = await self.download_and_store_file(url)
            audio_paths.append(temp)
        audio_path = self.concatenate_wave_files(audio_paths)
        data.add_field("audio", open(audio_path, "rb"))

        data.add_field("text", query.text)
        data.add_field("duration", self.calculate_audio_duration(audio_path))

        try:
            result = await self.make_authenticated_request(
                url="https://aligner.descript.com/", method="POST", data=data
            )
            return result
        except Exception as e:
            print(f"Failed transcript {str(e)}")

    async def get_assets(self):
        url = "https://api.descript.com/v2/projects/f734c6d7-e39d-4c1d-8f41-417f94cd37ce/media_assets?include_artifacts=true&cursor=1702016922390&include_placeholder=true"
        try:
            result = await self.make_authenticated_request(url)
            return result
        except Exception as e:
            print(f"Failed to get assets: {str(e)}")

    async def overdub_text(self, text, speaker="Lawrance", _voice_id=None):
        url = "https://api.descript.com/v2/projects/f734c6d7-e39d-4c1d-8f41-417f94cd37ce/overdub"
        voice_id = _voice_id or self.voice_ids[speaker]
        data = {
            "text": text,
            "voice_id": voice_id,
            "concatenate_audio": True,
            "tau_id": self.tau_id,
            "allow_prefix_expansion": True,
            "allow_suffix_expansion": True,
        }

        try:
            result = await self.make_authenticated_request(
                url, method="POST", data=data
            )
            return result
        except Exception as e:
            # Retry the request after refreshing the token if the failure is due to authorization
            if "authorization" in str(e).lower():
                await self.login_and_get_bearer_token()
                result = await self.make_authenticated_request(
                    url, method="POST", data=data
                )
                print(result)
                return result
            else:
                print(f"Failed to perform overdub: {str(e)}")

    async def overdub_staus(self, id):
        url = f"https://api.descript.com/v2/projects/f734c6d7-e39d-4c1d-8f41-417f94cd37ce/overdub/{id}"

        try:
            result = await self.make_authenticated_request(url, method="GET")
            print(result)
            return result
        except Exception as e:
            # Retry the request after refreshing the token if the failure is due to authorization
            if "authorization" in str(e).lower():
                await self.login_and_get_bearer_token()
                result = await self.make_authenticated_request(
                    url, method="POST", data=data
                )
                print(result)
                return result
            else:
                print(f"Failed to perform overdub: {str(e)}")

    async def request_status(self, id):
        status = await self.overdub_staus(id)
        if status["state"] == "done":
            asset_id = status["result"]["imputation_audio_asset_id"]
            overdub = await self.get_assets()
            for asset in overdub["data"]:
                if asset["id"] == asset_id:
                    data = TTSResponse(**asset)
                    url = data.artifacts[0].read_url
                    return {"url": url, "status": "done"}
        return status

    async def say(self, text, speaker="Henry"):
        overdub = await self.overdub_text(text, speaker=speaker)

        asset_id = None
        while True:
            status = await self.overdub_staus(overdub["id"])
            # print(status)
            if status["state"] == "done":
                # print(status)
                asset_id = status["result"]["imputation_audio_asset_id"]
                break
            await asyncio.sleep(3)

        overdub = await self.get_assets()
        for asset in overdub["data"]:
            if asset["id"] == asset_id:
                data = TTSResponse(**asset)
                url = data.artifacts[0].read_url
                print(url)
                path = await self.download_and_store_file(str(url))
                return path, url
