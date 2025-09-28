from domain.grnti.repository.repository import GrntiRepository
from domain.grnti.service.service import GrntiService
from domain.models.grnti import Grnti
from usecase.grnti.dto import GetGrntiDtoIn, GetGrntiDtoOut, SetGrntiDtoIn, DeleteGrntiDtoIn, SetGrntiDtoOut, \
    DeleteGrntiDtoOut, GetAllGrntiDtoOut, CreateGrntiDtoIn, CreateGrntiDtoOut


class GrntiUseCase:
    def __init__(self, grnti_repository: GrntiRepository, grnti_service: GrntiService):
        self.grnti_repository = grnti_repository
        self.expertService = grnti_service

    def get_grnti(self, dto_in: GetGrntiDtoIn) -> GetGrntiDtoOut:
        grnti = self.grnti_repository.get_grnti(dto_in.codrub)
        return GetGrntiDtoOut(
            codrub=grnti.codrub,
            description=grnti.description,
        )

    def set_grnti(self, dto_in: SetGrntiDtoIn) -> SetGrntiDtoOut:
        grnti = Grnti(
            codrub=dto_in.codrub,
            description=dto_in.description,
        )
        updated_grnti = self.grnti_repository.set_grnti(grnti)
        return SetGrntiDtoOut(
            codrub=updated_grnti.codrub,
            description=updated_grnti.description,
        )

    def delete_grnti(self, dto_in: DeleteGrntiDtoIn) -> DeleteGrntiDtoOut:
        deleted_grnti = self.grnti_repository.delete_grnti(dto_in.codrub)
        return DeleteGrntiDtoOut(
            codrub=deleted_grnti.codrub,
            description=deleted_grnti.description,
        )

    def get_all_grnti(self) -> list[GetAllGrntiDtoOut]:
        grnti_list = self.grnti_repository.get_all_grnti()
        result = list()
        for grnti in grnti_list:
            result.append(GetAllGrntiDtoOut(
                codrub=grnti.codrub,
                description=grnti.description,
            ))
        return result

    def create_grnti(self, dto_in: CreateGrntiDtoIn) -> CreateGrntiDtoOut:
        grnti = Grnti(
            codrub=dto_in.codrub,
            description=dto_in.description,
        )
        updated_grnti = self.grnti_repository.set_grnti(grnti)
        return CreateGrntiDtoOut(
            codrub=updated_grnti.codrub,
            description=updated_grnti.description,
        )
