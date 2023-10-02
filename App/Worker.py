from celery import Celery, chain
import os
import time
from App import celery_config
import yt_dlp
import tempfile
from App.Transcription.Utils.audio_transcription import transcribe_file
from App.Embedding.utils.Initialize import encode, generateChunks

celery = Celery()
celery.config_from_object(celery_config)


@celery.task(name="embbeding", bind=True)
def generate_store(self, data, task_id):
    chunks = generateChunks(data, task_id)
    encode(chunks)
    print("hellooo")


@celery.task(name="transcription", bind=True)
def transcription_task(self, file_path, model_size="tiny"):
    data = transcribe_file(state=self, file_path=file_path, model_size=model_size)
    generate_store.delay(data["content"], self.request.id)
    return data


@celery.task(name="download", bind=True)
def downloadfile(self, url, ydl_opts, model_size="base"):
    # updated
    self.update_state(state="Downloading File..", meta={})

    ####
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # updated
    self.update_state(state="Downloading complete", meta={})
    audio_file = ydl_opts["outtmpl"]
    print(model_size, "worker after")
    # print(audio_file["default"])
    data = transcribe_file(
        state=self, file_path=audio_file["default"], model_size=model_size
    )
    generate_store.delay(data["content"], self.request.id)
    return data
