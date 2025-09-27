from pydantic import BaseModel, Field
from datetime import datetime


class Expert(BaseModel):
    id: int
    name: str = Field(max_length=50, min_length=1)
    region: str = Field(max_length=50, min_length=1)
    city: str = Field(max_length=50, min_length=1)
    input_date: datetime
