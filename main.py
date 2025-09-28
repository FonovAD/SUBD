import sys

import psycopg2
from PySide6.QtWidgets import QApplication
from psycopg2.extensions import connection


from config import Config
from domain.expert.service.service import ExpertService
from domain.grnti.service.service import GrntiService
from domain.reg_obl_city.service.service import RegOblCityService
from infrastructure.storage.pg.expert.repository import ExpertRepository
from infrastructure.storage.pg.grnti.repository import GrntiRepository
from infrastructure.storage.pg.reg_obl_city.repository import RegOblCityRepository
from presentee.reg_obl_city import MainWindow
from usecase.expert.usecase import ExpertUseCase
from usecase.grnti.usecase import GrntiUseCase
from usecase.reg_obl_city.usecase import RegOblCityUseCase


def connect_to_db():
    try:
        db_config = Config().db_config

        connection = psycopg2.connect(
            host=db_config.host,
            port=db_config.port,
            database=db_config.name,
            user=db_config.user,
            password=db_config.password
        )

        print("Успешное подключение к базе данных!")
        return connection

    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


def main():
    connection = connect_to_db()
    print(1)
    usecase_expert = ExpertUseCase(
        ExpertRepository(connection),
        ExpertService()
    )
    usecase_grnti = GrntiUseCase(
        GrntiRepository(connection),
        GrntiService()
    )
    usecase_reg_obl_city = RegOblCityUseCase(
        RegOblCityRepository(connection),
        RegOblCityService()
    )

    app = QApplication(sys.argv)
    window = MainWindow(
        usecase_expert,
        usecase_grnti,
        usecase_reg_obl_city
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()