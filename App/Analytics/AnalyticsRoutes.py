from fastapi import APIRouter, status
from .Schemas import BaseRequest, editRequest
from .Model import Comments
from App.Users.Model import User
from App.Post.Model import Post

analytics_router = APIRouter(tags=["Analytics"])
