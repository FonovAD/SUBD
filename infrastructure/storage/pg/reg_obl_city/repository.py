from domain.reg_obl_city.repository.repository import RegOblCityRepository as repository
from domain.models.reg_obl_city import RegOblCity
import psycopg2
from psycopg2.extensions import connection

from infrastructure.storage.pg.reg_obl_city.templates import TEMPLATE_GET_REG_OBL_CITY, TEMPLATE_SET_REG_OBL_CITY, \
    TEMPLATE_DELETE_REG_OBL_CITY, TEMPLATE_GET_ALL_REG_OBL_CITY, TEMPLATE_CREATE_REG_OBL_CITY


class RegOblCityRepository(repository):
    def __init__(self, conn: connection):
        self.conn = conn

    def get_all_reg_obl_city(self) -> list[RegOblCity]:
        cursor = self.conn.cursor()
        reg_obl_city = list()
        try:
            cursor.execute(TEMPLATE_GET_ALL_REG_OBL_CITY)
            result = cursor.fetchall()
            for r in result:
                reg_obl_city.append(RegOblCity(
                    region=r[0],
                    oblname=r[1],
                    city=r[2]
                ))
            return reg_obl_city
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def get_reg_obl_city(self, city: str) -> RegOblCity:
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_GET_REG_OBL_CITY % city)
            result = cursor.fetchone()
            if result:
                return RegOblCity(
                    region=result[0],
                    oblname=result[1],
                    city=result[2]
                )
            return RegOblCity()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def set_reg_obl_city(self, reg_obl_city: RegOblCity) -> RegOblCity:
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_SET_REG_OBL_CITY % (reg_obl_city.region, reg_obl_city.oblname, reg_obl_city.city))
            result = cursor.fetchone()
            if result:
                return RegOblCity(
                    region=result[0],
                    oblname=result[1],
                    city=result[2]
                )
            return RegOblCity()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def delete_reg_obl_city(self, city: str) -> RegOblCity:
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_DELETE_REG_OBL_CITY % city)
            result = cursor.fetchone()
            if result:
                return RegOblCity(
                    region=result[0],
                    oblname=result[1],
                    city=result[2]
                )
            return RegOblCity()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()

    def create_reg_obl_city(self, reg_obl_city : RegOblCity) -> RegOblCity:
        cursor = self.conn.cursor()
        try:
            cursor.execute(TEMPLATE_CREATE_REG_OBL_CITY % (reg_obl_city.region, reg_obl_city.oblname, reg_obl_city.city))
            result = cursor.fetchone()
            if result:
                return RegOblCity(
                    region=result[0],
                    oblname=result[1],
                    city=result[2]
                )
            return RegOblCity()
        except (Exception, psycopg2.Error) as error:
            print(error)
            raise error
        finally:
            cursor.close()
