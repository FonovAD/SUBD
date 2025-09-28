from pydantic import BaseModel


class GetGrntiDtoIn(BaseModel):
    codrub: int


class GetGrntiDtoOut(BaseModel):
    codrub: int
    description: str


class SetGrntiDtoIn(BaseModel):
    codrub: int
    description: str


class SetGrntiDtoOut(BaseModel):
    codrub: int
    description: str


class DeleteGrntiDtoIn(BaseModel):
    codrub: int


class DeleteGrntiDtoOut(BaseModel):
    codrub: int
    description: str

class GetAllGrntiDtoOut(BaseModel):
    codrub: int
    description: str
