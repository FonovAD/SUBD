from abc import ABC, abstractmethod

from domain.models.reg_obl_city import RegOblCity


class RegOblCityRepository(ABC):

    @abstractmethod
    def get_all_reg_obl_city(self) -> list[RegOblCity]:
        pass

    @abstractmethod
    def get_reg_obl_city(self, city: str) -> RegOblCity:
        pass

    @abstractmethod
    def set_reg_obl_city(self, reg_obl_city: RegOblCity) -> RegOblCity:
        pass

    @abstractmethod
    def delete_reg_obl_city(self, city: str) -> RegOblCity:
        pass

    @abstractmethod
    def create_reg_obl_city(self, reg_obl_city: RegOblCity) -> RegOblCity:
        pass