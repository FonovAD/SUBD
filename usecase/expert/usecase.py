from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from domain.expert.repository.repository import ExpertRepository
from domain.expert.service.service import ExpertService
from domain.models.expert import Expert
from domain.models.expert_grnti import ExpertGrnti

from usecase.expert.dto import CreateExpertWithGrntiDtoOut, GetExpertWithGrntiDtoIn, GetExpertWithGrntiDtoOut, \
    GetAllExpertWithGrntiDtoOut, SetExpertGrntiDtoOut, SetExpertGrntiDtoIn, DeleteExpertDtoOut, DeleteExpertDtoIn, \
    SetExpertDtoOut, SetExpertDtoIn, GetExpertDtoOut, GetExpertDtoIn, CreateExpertWithGrntiDtoIn


class ExpertUseCase:
    def __init__(self, expert_repository: ExpertRepository, expert_service: ExpertService):
        self.expertRepository = expert_repository
        self.expertService = expert_service

    def get_expert(self, dto_in: GetExpertDtoIn) -> GetExpertDtoOut:
        """Получение эксперта по ID"""
        expert = self.expertRepository.get_expert(dto_in.id)

        if not expert or expert.id == 0:
            raise Exception(f'Expert with id {dto_in.id} not found')

        return GetExpertDtoOut(
            id=expert.id,
            name=expert.name,
            region=expert.region,
            city=expert.city,
            input_date=expert.input_date
        )

    def get_all_expert(self) -> list[Expert]:
        """ Получение всех пользователей"""
        result = list()
        experts = self.expertRepository.get_all_expert()
        for e in experts:
            result.append(GetExpertDtoOut(
                id=e.id,
                name=e.name,
                region=e.region,
                city=e.city,
                input_date=e.input_date
            ))
        return result

    def set_expert(self, dto_in: SetExpertDtoIn) -> SetExpertDtoOut:
        """Изменение параметров эксперта"""
        expert = Expert(
            id=dto_in.id,
            name=dto_in.name,
            region=dto_in.region,
            city=dto_in.city,
            input_date=dto_in.input_date
        )

        if not self.expertService.validate_expert(expert):
            raise Exception('Invalid expert data')

        updated_expert = self.expertRepository.set_expert(expert)

        if not updated_expert or updated_expert.id == 0:
            raise Exception('Failed to update expert')

        return SetExpertDtoOut(
            id=updated_expert.id,
            name=updated_expert.name,
            region=updated_expert.region,
            city=updated_expert.city,
            input_date=updated_expert.input_date
        )

    def delete_expert(self, dto_in: DeleteExpertDtoIn) -> DeleteExpertDtoOut:
        """Удаление эксперта"""
        deleted_expert = self.expertRepository.delete_expert(dto_in.id)

        if not deleted_expert or deleted_expert.id == 0:
            raise Exception(f'Expert with id {dto_in.id} not found or already deleted')

        return DeleteExpertDtoOut(
            id=deleted_expert.id,
            name=deleted_expert.name,
            region=deleted_expert.region,
            city=deleted_expert.city,
            input_date=deleted_expert.input_date
        )

    def create_expert_with_grnti(self, dto_in: CreateExpertWithGrntiDtoIn) -> CreateExpertWithGrntiDtoOut:
        """Создание эксперта с несколькими кодами ГРНТИ"""
        expert = Expert(
            id=0,
            name=dto_in.name,
            region=dto_in.region,
            city=dto_in.city,
            input_date=dto_in.input_date
        )

        if not self.expertService.validate_expert(expert):
            raise Exception('Invalid expert data')

        grnti_list = []
        for grnti_data in dto_in.grnti_list:
            try:
                grnti = ExpertGrnti(
                    expertID=0,
                    rubric=grnti_data.rubric,
                    subrubric=grnti_data.subrubric,
                    discipline=grnti_data.discipline
                )
                grnti_list.append(grnti)
            except Exception as e:
                raise Exception(f'Invalid GRNTI data: {e}')

        expert_with_grnti_records = self.expertRepository.create_expert_with_grnti(expert, grnti_list)

        if not expert_with_grnti_records:
            raise Exception('Failed to create expert with GRNTI')

        created_expert = expert_with_grnti_records[0].expert if expert_with_grnti_records else expert

        return CreateExpertWithGrntiDtoOut(
            expert=created_expert,
            grnti_list=expert_with_grnti_records
        )

    def get_expert_with_grnti(self, dto_in: GetExpertWithGrntiDtoIn) -> GetExpertWithGrntiDtoOut:
        """Получение эксперта по ID с его кодами ГРНТИ"""
        expert_with_grnti = self.expertRepository.get_expert_with_grnti(dto_in.id)

        if not expert_with_grnti or not expert_with_grnti.expert or expert_with_grnti.expert.id == 0:
            raise Exception(f'Expert with id {dto_in.id} not found')

        return GetExpertWithGrntiDtoOut(
            expert_with_grnti=expert_with_grnti
        )

    def set_expert_grnti(self, dto_in: SetExpertGrntiDtoIn) -> SetExpertGrntiDtoOut:
        """Изменение кода ГРНТИ эксперта"""
        expert = self.expertRepository.get_expert(dto_in.expert_id)
        if not expert or expert.id == 0:
            raise Exception(f'Expert with id {dto_in.expert_id} not found')

        try:
            grnti = ExpertGrnti(
                expertID=dto_in.expert_id,
                rubric=dto_in.rubric,
                subrubric=dto_in.subrubric,
                discipline=dto_in.discipline
            )
        except Exception as e:
            raise Exception(f'Invalid GRNTI data: {e}')

        updated_grnti = self.expertRepository.set_expert_grnti(expert, grnti)

        if not updated_grnti or updated_grnti.expertID == 0:
            raise Exception('Failed to update expert GRNTI')

        return SetExpertGrntiDtoOut(
            expert_grnti=updated_grnti
        )

    def get_all_expert_with_grnti(self) -> GetAllExpertWithGrntiDtoOut:
        """Получение всех экспертов с их ГРНТИ и расшифровкой"""
        experts_with_grnti = self.expertRepository.get_all_expert_with_grnti()

        return GetAllExpertWithGrntiDtoOut(
            experts=experts_with_grnti
        )

    def validate_expert_data(self, name: str, region: str, city: str) -> bool:
        """Валидация данных эксперта (удобный метод для предварительной проверки)"""
        try:
            temp_expert = Expert(
                id=0,
                name=name,
                region=region,
                city=city,
                input_date=datetime.now()
            )
            return self.expertService.validate_expert(temp_expert)
        except Exception:
            return False
