from pydantic import BaseModel, Field

from domain.models.expert import Expert


class ExpertGrnti(BaseModel):
    expertID : int
    rubric: int = Field(lt=100)
    subrubric : int = Field(lt=100)
    discipline : int = Field(lt=100)