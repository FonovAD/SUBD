from infrastructure.storage.pg.expert.templates import TEMPLATE_DELETE_EXPERT

TEMPLATE_GET_GRNTI = """
SELECT codrub, description 
FROM grnti_classifier 
WHERE codrub = %d;
"""

TEMPLATE_SET_GRNTI = """
UPDATE grnti_classifier 
SET description = %s 
WHERE codrub = %d
RETURNING codrub, description;
"""

TEMPLATE_DELETE_GRNTI = """
DELETE FROM grnti_classifier 
WHERE codrub = %d 
RETURNING codrub, description;
"""

TEMPLATE_GET_ALL_GRNTI = """
SELECT codrub, description 
FROM grnti_classifier 
ORDER BY codrub;
"""