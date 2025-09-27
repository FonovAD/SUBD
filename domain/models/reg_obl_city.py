from pydantic import BaseModel, Field


class RegOblCity(BaseModel):
    region: str = Field(max_length=100, min_length=1)
    oblname: str = Field(max_length=100, min_length=1)
    city: str = Field(max_length=100, min_length=1)
