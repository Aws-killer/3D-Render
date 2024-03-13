import gradio as gr
import asyncio
import copy
import json
import base64
from io import BytesIO
import IPython.display as ipd
from watchgod import awatch
from Complete import (
    Speak,
    Transcriber,
    MovieDescriptionProcessor,
)  # Replace 'your_script' with your actual module name

tts_client = Speak()
movie_processor = MovieDescriptionProcessor()


# Gradio app function
def gradio_app(movie_name, year, media_type, original_language, go_button):
    if go_button:
        print("here")
        # Construct the message for movie description
        message = movie_processor.prompt_fetcher()
        message = message.format(
            media_type=media_type,
            movie_name=movie_name,
            original_language=original_language,
            movie_year=year,
        )

        # Process movie description
        script = asyncio.run(movie_processor.process_movie_description(message))

        # Generate image descriptions
        message, result = movie_processor.prompt_fetcher("images").split("{format}")
        message = message.format(script=script) + result
        images_descriptions = asyncio.run(
            movie_processor.process_movie_description(message, "Assistant")
        )
        image_json = movie_processor.extract_json_from_markdown(images_descriptions)

        # Generate audio file
        audio_file_path = asyncio.run(tts_client.say(script))

        # Create an instance of the Transcriber class
        transcriber = Transcriber(audio_file_path)

        # Perform the transcription task
        asyncio.run(transcriber.transcribe())

        # Download the JSON transcription to a file
        output_json_path = "./output.json"  # Replace with the desired output path
        asyncio.run(transcriber.download_transcription(output_json_path))

        # Return the outputs
        return {
            "image_json": image_json,
            "audio_file": {"name": "audio_file.wav", "file_path": audio_file_path},
            "tts_json": {"name": "tts_output.json", "file_path": output_json_path},
        }
    return None


# Define Gradio inputs
inputs = [
    gr.Textbox(placeholder="Avatar", label="Movie Name"),
    gr.Textbox(placeholder="2023", label="Year"),
    gr.Radio(choices=["movie", "tv series"], label="Media Type"),
    gr.Dropdown(choices=["English", "Spanish"], label="Original Language"),
    gr.Button("go_button"),
]


# Define Gradio outputs
outputs = [
    gr.Textbox("image_json", label="Image JSON"),
    # gr.File("audio_file", label="Audio File"),
    # gr.File("tts_json", label="TTS JSON")
]

# Create the Gradio interface
iface = gr.Interface(fn=gradio_app, inputs=inputs, outputs=outputs, live=True)


# Launch the Gradio app
async def restart_gradio():
    async for changes in awatch(".", watcher_cls=watchgod.DefaultDirWatcher):
        await iface.close()
        iface.launch()


# Run Gradio interface and hot-reloading
loop = asyncio.get_event_loop()
loop.create_task(restart_gradio())
iface.launch()
