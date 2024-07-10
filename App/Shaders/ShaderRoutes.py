from fastapi import APIRouter, status, BackgroundTasks
from .Schemas import BaseRequest, BaseResponse
from fastapi import FastAPI, HTTPException, Request
import os, uuid

# from HuggingChat import getChatBot


import aiofiles
from fastapi.responses import StreamingResponse, FileResponse
from .utils import make_effect

shader_router = APIRouter(tags=["Shaders"])


@shader_router.get("/3d-effect")
async def shader_3d(image_link: str, background_task: BackgroundTasks):
    filename = f"{str(uuid.uuid4())}.mp4"
    background_task.add_task(make_effect, image_link=image_link, filename=filename)
    return filename


@shader_router.get("/shaderOuput/{audio_name}")
async def serve_audio(request: Request, audio_name: str):
    audio_directory = "/tmp/Video"
    audio_path = os.path.join(audio_directory, audio_name)
    if not os.path.isfile(audio_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    range_header = request.headers.get("Range", None)
    audio_size = os.path.getsize(audio_path)

    if range_header:
        start, end = range_header.strip().split("=")[1].split("-")
        start = int(start)
        end = audio_size if end == "" else int(end)

        headers = {
            "Content-Range": f"bytes {start}-{end}/{audio_size}",
            "Accept-Ranges": "bytes",
            # Optionally, you might want to force download by uncommenting the next line:
            # "Content-Disposition": f"attachment; filename={audio_name}",
        }

        content = read_file_range(audio_path, start, end)
        return StreamingResponse(content, media_type="video/mp4", headers=headers)

    return FileResponse(audio_path, media_type="video/mp4")


async def read_file_range(path, start, end):
    async with aiofiles.open(path, "rb") as file:
        await file.seek(start)
        while True:
            data = await file.read(1024 * 1024)  # read in chunks of 1MB
            if not data or await file.tell() > end:
                break
            yield data
