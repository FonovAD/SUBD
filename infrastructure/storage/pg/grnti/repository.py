from domain.grnti.repository.repository import GrntiRepository as repository
import psycopg2
from psycopg2.extensions import connection
from domain.models.grnti import Grnti
from infrastructure.storage.pg.grnti.templates import TEMPLATE_GET_GRNTI, TEMPLATE_SET_GRNTI, TEMPLATE_DELETE_GRNTI, \
    TEMPLATE_GET_ALL_GRNTI, TEMPLATE_CREATE_GRNTI


class GrntiRepository(repository):
    def __init__(self, conn: connection):
        self.conn = conn

    def get_grnti(self, codrub: int) -> Grnti:
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_GET_GRNTI % codrub)
            result = cursor.fetchone()
            if result:
                return Grnti(
                    codrub=result[0],
                    description=result[1],
                )
            return Grnti()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def set_grnti(self, grnti: Grnti) -> Grnti:
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_SET_GRNTI % (grnti.codrub, grnti.description))
            result = cursor.fetchone()
            if result:
                return Grnti(
                    codrub=result[0],
                    description=result[1],
                )
            return Grnti()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def delete_grnti(self, codrub: int) -> Grnti:
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_DELETE_GRNTI % codrub)
            result = cursor.fetchone()
            if result:
                return Grnti(
                    codrub=result[0],
                    description=result[1],
                )
            return Grnti()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def get_all_grnti(self) -> list[Grnti]:
        cursor = self.conn.cursor()
        grnti = list()
        try:
            cursor.execute(TEMPLATE_GET_ALL_GRNTI)
            result = cursor.fetchall()
            for r in result:
                grnti.append(
                    Grnti(
                        codrub=r[0],
                        description=r[1],
                    ))
            return grnti
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def create_grnti(self, grnti: Grnti) -> Grnti:
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_CREATE_GRNTI % (grnti.codrub, grnti.description))
            result = cursor.fetchone()
            if result:
                return Grnti(
                    codrub=result[0],
                    description=result[1],
                )
            return Grnti()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()
