import re

from domain.models.reg_obl_city import RegOblCity


class RegOblCityService():

    def validate_reg_obl_city(self, reg_obl_city: RegOblCity) -> bool:
        reg_city_pattern = r'^[А-Яа-яЁё\-]+$'
        return bool(
            re.match(reg_city_pattern, reg_obl_city.city) and
            re.match(reg_city_pattern, reg_obl_city.region) and
            re.match(reg_city_pattern, reg_obl_city.oblname)
        )
