from abc import ABC, abstractmethod

from domain.models.expert import Expert
from domain.models.expert_with_grnti import ExpertWithGrnti
from domain.models.user_grnti import ExpertGrnti


class ExpertRepository:

    @abstractmethod
    def get_expert(self, expert_id: int) -> Expert:
        """ Получение пользователя по ID"""
        pass

    @abstractmethod
    def set_expert(self, expert: Expert) -> Expert:
        """ Изменение параметров пользователя"""
        pass

    @abstractmethod
    def delete_expert(self, expert_id: int) -> Expert:
        """ Удаление пользователя"""
        pass

    @abstractmethod
    def create_expert_with_grnti(self, expert: Expert, grnti_list : list[ExpertGrnti]) -> ExpertWithGrnti:
        """ Создание пользователя с несколькими кодами ГРНТИ"""
        pass

    @abstractmethod
    def get_expert_with_grnti(self, expert_id: int) -> ExpertWithGrnti:
        """ Получение пользователя по ID с его кодами ГРНТИ"""
        pass

    @abstractmethod
    def set_expert_grnti(self, expert: Expert, grnti : ExpertGrnti) -> ExpertWithGrnti:
        """ Изменение кода ГРНТИ эксперта"""
        pass

    @abstractmethod
    def get_all_expert_with_grnti(self) -> list[ExpertWithGrnti]:
        """ Получение всех пользователей с их ГРНТИ и расшифровкой"""
        pass
