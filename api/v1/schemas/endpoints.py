from pydantic import BaseModel
from pydantic.networks import HttpUrl


class EndpointModel(BaseModel):
    url: HttpUrl

    class Config:
        orm_mode = True
