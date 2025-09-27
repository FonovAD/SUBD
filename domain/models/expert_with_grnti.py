from pydantic import BaseModel

from domain.models.expert import Expert
from domain.models.grnti import Grnti
from domain.models.expert_grnti import ExpertGrnti


class ExpertWithGrnti(BaseModel):
    expert: Expert
    expert_grnti: ExpertGrnti
    grnti: Grnti
