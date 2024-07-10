import os
import os

os.makedirs("/usr/local/lib/python3.10/site-packages/Workspace", exist_ok=True)
os.environ["WINDOW_BACKEND"] = "headless"  # Use software rendering
os.environ["SKIP_TORCH"] = "1"

from DepthFlow import DepthFlowScene
import uuid


depthflow = DepthFlowScene()


def make_effect(image_link, filename: str):

    destination = os.path.join("/tmp/Video", filename)
    depthflow.input(image=image_link)
    depthflow.main(
        fps=30,
        output=destination,
        quality=1,
    )
    return {"file": filename}
