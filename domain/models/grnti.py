from pydantic import BaseModel, Field


class Grnti(BaseModel):
    codrub: int = Field(ge=0, le=100)
    description: str = Field(max_length=100)
