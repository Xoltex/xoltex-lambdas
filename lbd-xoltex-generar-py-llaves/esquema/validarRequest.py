from pydantic import BaseModel, Field, ValidationError
from typing import Optional

class HeadersSchema(BaseModel):
    Authorization: str = Field(..., min_length=10)

class BodySchema(BaseModel):
    nombre: str
    edad: int

class PathParamsSchema(BaseModel):
    llaves: str
