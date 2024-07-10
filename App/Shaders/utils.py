import os

os.environ["WINDOW_BACKEND"] = "headless"  # Use software rendering
os.environ["SKIP_TORCH"] = "1"

from DepthFlow import DepthFlowScene
import uuid


depthflow = DepthFlowScene()


def make_effect(image_link):
    filename = f"{str(uuid.uuid4())}.mp4"
    destination = os.path.join("/tmp/Video", filename)
    depthflow.input(image=image_link)
    depthflow.main(
        fps=30,
        output=destination,
        quality=1,
    )
    return {"file": filename}
