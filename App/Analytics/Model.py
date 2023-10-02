import asyncio
import orm
import psycopg2
import datetime
import pydantic
from App.modelInit import database, models
from App.Users.Model import User


class Analytics(orm.Model):
    tablename = "Analytics"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "user": orm.ForeignKey(
            User, on_delete=orm.CASCADE, allow_null=True
        ),  # Optional for unknown users.
        "post": orm.ForeignKey(User, on_delete=orm.CASCADE),
        "ip": orm.String(max_length=100),
        "device": orm.String(max_length=100),
        "country": orm.String(max_length=100),
        "createdAt": orm.DateTime(index=True, default=datetime.datetime.now),
    }
