
TEMPLATE_GET_ALL_REG_OBL_CITY = """
SELECT region, oblname, city 
FROM reg_obl_city 
ORDER BY region, oblname, city;
"""

TEMPLATE_GET_REG_OBL_CITY = """
SELECT region, oblname, city 
FROM reg_obl_city 
WHERE city = %s;
"""

TEMPLATE_SET_REG_OBL_CITY = """
UPDATE reg_obl_city 
SET region = %s, oblname = %s 
WHERE city = %s 
RETURNING region, oblname, city;
"""


TEMPLATE_DELETE_REG_OBL_CITY = """
DELETE FROM reg_obl_city 
WHERE city = %s 
RETURNING region, oblname, city;
"""


TEMPLATE_CREATE_REG_OBL_CITY = """
INSERT INTO reg_obl_city (region, oblname, city)
VALUES (%s, %s, %s)
RETURNING region, oblname, city;
"""
