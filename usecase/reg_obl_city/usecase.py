from domain.reg_obl_city.repository.repository import RegOblCityRepository
from domain.reg_obl_city.service.service import RegOblCityService
from domain.models.reg_obl_city import RegOblCity
from usecase.reg_obl_city.dto import GetRegOblCityDtoOut, GetRegOblCityDtoIn, SetRegOblCityDtoIn, SetRegOblCityDtoOut, \
    DeleteRegOblCityDtoIn, DeleteRegOblCityDtoOut


class RegOblCityUseCase():
    def __init__(self, reg_obl_city_repository: RegOblCityRepository, reg_obl_city_service: RegOblCityService):
        self.reg_obl_city_repository = reg_obl_city_repository
        self.reg_obl_city_service = reg_obl_city_service

    def get_all_reg_obl_city(self) -> list[GetRegOblCityDtoOut]:
        result = []
        roc =  self.reg_obl_city_repository.get_all_reg_obl_city()
        for r in roc:
            result.append(GetRegOblCityDtoOut(
                region=r.region,
                city=r.city,
                oblname=r.oblname,
            ))
        return result

    def get_reg_obl_city(self, dto_in: GetRegOblCityDtoIn) -> GetRegOblCityDtoOut:
        roc = self.reg_obl_city_repository.get_reg_obl_city(dto_in.city)
        return GetRegOblCityDtoOut(
            region=roc.region,
            city=roc.city,
            oblname=roc.oblname,
        )


    def set_reg_obl_city(self, dto_in: SetRegOblCityDtoIn) -> SetRegOblCityDtoOut:
        roc = RegOblCity(
            region=dto_in.region,
            city=dto_in.city,
            oblname=dto_in.oblname,
        )
        if not self.reg_obl_city_service.validate_reg_obl_city(roc):
            raise Exception("Invalid reg obl city")
        updated_roc = self.reg_obl_city_repository.set_reg_obl_city(roc)
        return SetRegOblCityDtoOut(
            region=updated_roc.region,
            city=updated_roc.city,
            oblname=updated_roc.oblname,
        )


    def delete_reg_obl_city(self, dto_in: DeleteRegOblCityDtoIn) -> DeleteRegOblCityDtoOut:
        deleted_roc = self.reg_obl_city_repository.delete_reg_obl_city(dto_in.city)
        return DeleteRegOblCityDtoOut(
            region=deleted_roc.region,
            city=deleted_roc.city,
            oblname=deleted_roc.oblname,
        )