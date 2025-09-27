import re

from domain.models.expert import Expert


class ExpertService():

    def validate_expert(self, expert: Expert) -> bool:
        name_pattern = r'^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.[А-ЯЁ]\.$'
        reg_city_pattern = r'^[А-Яа-яЁё\-]+$'
        return bool(
            re.match(name_pattern, expert.name) and
            re.match(reg_city_pattern, expert.city) and
            re.match(reg_city_pattern, expert.region)
        )
