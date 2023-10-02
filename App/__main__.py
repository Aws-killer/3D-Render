from App.app import app

import uvicorn
import asyncio


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
