from pydantic import BaseModel


class GetRegOblCityDtoIn(BaseModel):
    city: str


class GetRegOblCityDtoOut(BaseModel):
    region: str
    oblname: str
    city: str


class SetRegOblCityDtoIn(BaseModel):
    region: str
    oblname: str
    city: str


class SetRegOblCityDtoOut(BaseModel):
    region: str
    oblname: str
    city: str


class DeleteRegOblCityDtoIn(BaseModel):
    city: str


class DeleteRegOblCityDtoOut(BaseModel):
    region: str
    oblname: str
    city: str