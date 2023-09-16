# This is a contrived example of BaseEndpointResponse usage

from pydantic import BaseModel

import app.schemas.shared


class User(BaseModel):
    name: str
    email: str


class ReadResponse(app.schemas.shared.BaseEndpointResponse):
    user: User


class ReadManyResponse(app.schemas.shared.BaseEndpointResponse):
    users: list[User]
