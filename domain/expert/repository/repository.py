from abc import ABC, abstractmethod

from domain.models.expert import Expert


class ExpertRepository:

    @abstractmethod
    def get_expert(self, expert_id: int) -> Expert:
        pass

    @abstractmethod
    def set_expert(self, expert: Expert) -> Expert:
        pass

    @abstractmethod
    def delete_expert(self, expert_id: int) -> Expert:
        pass
