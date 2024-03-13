# ---
# lambda-test: false
# ---
# # Stable Diffusion (A1111)
#
# This example runs the popular [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
# project on Modal, without modification. We start a Modal container with an A10G GPU, run the server as a
# subprocess, and forward the port using a [tunnel](/docs/guide/tunnels).

import socket
import subprocess
import time
import webbrowser

from modal import Image, Queue, Stub, forward

stub = Stub("fooocus")
stub.urls = Queue.new()  # TODO: FunctionCall.get() doesn't support generators.


def wait_for_port(port: int):
    while True:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=5.0):
                break
        except OSError:
            time.sleep(0.1)


# The following function starts the web UI container. Notice that it requires a few steps to
# install dependencies, since `stable-diffusion-webui` doesn't come with a prepackaged script
# to do this. (It usually installs dependencies on first launch.)
#
# After defining the custom container image, we start the server with `accelerate launch`. This
# function is also where you would configure hardware resources, CPU/memory, and timeouts.
#
# If you want to run it with an A100 GPU, just change `gpu="a10g"` to `gpu="a100"`.


@stub.function(
    image=Image.debian_slim()
    .apt_install("wget", "git")
    .run_commands(
        "pip install pygit2==1.12.2",
        "git clone https://github.com/lllyasviel/Fooocus.git",
        "pip install -r /Fooocus/requirements_versions.txt",
        gpu="a10g",
    ),
    gpu="a10g",
    cpu=2,
    memory=1024,
    timeout=3600,
)
def start_web_ui():
    START_COMMAND = r"""
        python /Fooocus/entry_with_update.py --share
"""
    with forward(7860) as tunnel:
        p = subprocess.Popen(START_COMMAND, shell=True)
        wait_for_port(7860)
        print("[MODAL] ==> Accepting connections at", tunnel.url)
        stub.urls.put(tunnel.url)
        p.wait(3600)


# The first run may take a few minutes to build the image. When the container starts, it will open
# the page in your browser.


@stub.local_entrypoint()
def main(no_browser: bool = False):
    start_web_ui.spawn()
    url = stub.urls.get()
    if not no_browser:
        webbrowser.open(url)
    while True:  # TODO: FunctionCall.get() doesn't support generators.
        time.sleep(1)
