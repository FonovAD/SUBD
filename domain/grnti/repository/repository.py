from abc import ABC, abstractmethod

from domain.models.grnti import Grnti


class GrntiRepository(ABC):

    @abstractmethod
    def get_grnti(self, codrub: int) -> Grnti:
        pass

    @abstractmethod
    def set_grnti(self, grnti: Grnti) -> Grnti:
        pass

    @abstractmethod
    def delete_grnti(self, codrub: int) -> Grnti:
        pass

    @abstractmethod
    def get_all_grnti(self) -> list[Grnti]:
        pass