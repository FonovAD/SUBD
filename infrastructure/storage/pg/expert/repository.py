import datetime

import psycopg2
from psycopg2.extensions import connection

import domain.expert.repository.repository as repository
from domain.models.expert import Expert
from domain.models.expert_with_grnti import ExpertWithGrnti
from domain.models.grnti import Grnti
from domain.models.expert_grnti import ExpertGrnti
from infrastructure.storage.pg.expert.templates import TEMPLATE_GET_EXPERT, TEMPLATE_SET_EXPERT, \
    TEMPLATE_DELETE_EXPERT, TEPLATE_CREATE_GRNTI_EXPERT, TEMPLATE_GET_EXPERT_WITH_GRNTI, TEMPLATE_SET_EXPERT_GRNTI, \
    TEMPLATE_GET_ALL_WITH_GRNTI


class ExpertRepository(repository):
    def __init__(self, conn: connection):
        self.conn = conn

    def get_expert(self, expert_id: int) -> Expert:
        """ Получение пользователя по ID"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_GET_EXPERT % expert_id)
            result = cursor.fetchone()
            if result:
                return Expert(
                    id=result[0],
                    name=result[1],
                    region=result[2],
                    city=result[3],
                    input_date=result[4]
                )
            return Expert()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def set_expert(self, expert: Expert) -> Expert:
        """ Изменение параметров пользователя"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_SET_EXPERT % (expert.name, expert.region, expert.city, datetime.date.today()))
            result = cursor.fetchone()
            if result:
                return Expert(
                    id=result[0],
                    name=result[1],
                    region=result[2],
                    city=result[3],
                    input_date=result[4]
                )
            return Expert()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def delete_expert(self, expert_id: int) -> Expert:
        """ Удаление пользователя"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_DELETE_EXPERT % expert_id)
            result = cursor.fetchone()
            if result:
                return Expert(
                    id=result[0],
                    name=result[1],
                    region=result[2],
                    city=result[3],
                    input_date=result[4]
                )
            return Expert()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def create_expert_with_grnti(self, expert: Expert, grnti_list: list[ExpertGrnti]) -> list[ExpertWithGrnti]:
        """ Создание пользователя с несколькими кодами ГРНТИ"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_DELETE_EXPERT % (expert.name, expert.region, expert.city, datetime.date.today()))
            result = cursor.fetchone()

            expert.id = result[0]

            expertWithGrntiRecords = list()

            for grnti in grnti_list:
                cursor.execute(
                    TEPLATE_CREATE_GRNTI_EXPERT % (expert.id, grnti.rubric, grnti.subrubric, grnti.discipline)
                )
                result = cursor.fetchone()
                if result:
                    expertWithGrntiRecords.append(ExpertWithGrnti(
                        expert=expert,
                        grnti=Grnti(
                            codrub=result[0],
                            description=result[3]),
                        expert_grnti=grnti
                    ))
            return expertWithGrntiRecords
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def get_expert_with_grnti(self, expert_id: int) -> ExpertWithGrnti:
        """ Получение пользователя по ID с его кодами ГРНТИ"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_GET_EXPERT_WITH_GRNTI % expert_id)
            result = cursor.fetchone()
            if result:
                return ExpertWithGrnti(
                    expert=Expert(
                        id=result[0],
                        name=result[1],
                        region=result[2],
                        city=result[3],
                        input_date=result[4]),
                    expert_grnti=ExpertGrnti(
                        expertID=result[0],
                        rubric=result[5],
                        subrubric=result[6],
                        discipline=result[7],
                    ),
                    grnti=Grnti(
                        codrub=result[5],
                        description=result[8],
                    )
                )
            return ExpertWithGrnti()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def set_expert_grnti(self, expert: Expert, grnti: ExpertGrnti) -> ExpertGrnti:
        """ Изменение кода ГРНТИ эксперта"""
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_SET_EXPERT_GRNTI % (grnti.rubric, grnti.subrubric, grnti.discipline, expert.id))
            result = cursor.fetchone()
            if result:
                return ExpertGrnti(
                    expertID=result[0],
                    rubric=result[1],
                    subrubric=result[2],
                    discipline=result[3],
                )
            return ExpertGrnti()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def get_all_expert_with_grnti(self) -> list[ExpertWithGrnti]:
        """ Получение всех пользователей с их ГРНТИ и расшифровкой"""
        cursor = self.conn.cursor()
        expertWithGrntiRecords = list()
        try:
            cursor.execute(TEMPLATE_GET_ALL_WITH_GRNTI)
            result = cursor.fetchall()
            for r in result:
                expertWithGrntiRecords.append(
                    ExpertWithGrnti(
                        expert=Expert(
                            id=result[0],
                            name=result[1],
                            region=result[2],
                            city=result[3],
                            input_date=result[4]),
                        expert_grnti=ExpertGrnti(
                            expertID=result[0],
                            rubric=result[5],
                            subrubric=result[6],
                            discipline=result[7],
                        ),
                        grnti=Grnti(
                            codrub=result[5],
                            description=result[8],
                        )
                ))
            return expertWithGrntiRecords()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()
