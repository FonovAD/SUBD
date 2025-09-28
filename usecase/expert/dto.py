from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from domain.models.expert import Expert
from domain.models.expert_grnti import ExpertGrnti
from domain.models.expert_with_grnti import ExpertWithGrnti

class GetExpertDtoIn(BaseModel):
    id: int


class SetExpertDtoIn(BaseModel):
    id: int
    name: str
    region: str
    city: str
    input_date: datetime


class DeleteExpertDtoIn(BaseModel):
    id: int


class CreateExpertWithGrntiDtoIn(BaseModel):

    class Grnti(BaseModel):
        rubric: int
        subrubric: int
        discipline: int

    name: str
    region: str
    city: str
    input_date: datetime
    grnti_list: list[Grnti]


class GetExpertWithGrntiDtoIn(BaseModel):
    id: int


class SetExpertGrntiDtoIn(BaseModel):
    expert_id: int
    rubric: int
    subrubric: Optional[int] = None
    discipline: Optional[int] = None

class GetExpertDtoOut(BaseModel):
    id: int
    name: str
    region: str
    city: str
    input_date: datetime


class SetExpertDtoOut(BaseModel):
    id: int
    name: str
    region: str
    city: str
    input_date: datetime


class DeleteExpertDtoOut(BaseModel):
    id: int
    name: str
    region: str
    city: str
    input_date: datetime


class CreateExpertWithGrntiDtoOut(BaseModel):
    expert: Expert
    grnti_list: list[ExpertWithGrnti]


class GetExpertWithGrntiDtoOut(BaseModel):
    expert_with_grnti: ExpertWithGrnti


class SetExpertGrntiDtoOut(BaseModel):
    expert_grnti: ExpertGrnti


class GetAllExpertWithGrntiDtoOut(BaseModel):
    experts: list[ExpertWithGrnti]
