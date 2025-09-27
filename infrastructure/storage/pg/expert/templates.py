

TEMPLATE_GET_EXPERT = """
SELECT (id, name, region, city, input_date) FROM expert WHERE id = %s;
"""

TEMPLATE_SET_EXPERT = """
UPDATE expert SET name = %s, region = %s, city = %s, input_date = %s WHERE id = %d;
RETURNING id, name, region, city, input_date;
"""

TEMPLATE_DELETE_EXPERT = """
DELETE FROM expert WHERE id = %d
RETURNING id, name, region, city, input_date;
"""

TEMPLATE_CREATE_EXPERT = """
INSERT INTO expert (name, region, city, input_date) VALUES (%s, %s, %s, %s)
RETURNING id;
"""

TEPLATE_CREATE_GRNTI_EXPERT = """
WITH inserted_grnti AS (
    INSERT INTO expert_grnti (id, rubric, subrubric, discipline) 
    VALUES (%d, %s, %s, %s)
    RETURNING id, rubric, subrubric, discipline
)
SELECT ig.rubric, ig.subrubric, ig.discipline, gc.description 
FROM inserted_grnti ig
JOIN grnti_classifier gc ON ig.rubric = gc.codrub;
"""

TEMPLATE_GET_EXPERT_WITH_GRNTI = """
SELECT 
    expert.id, 
    expert.name, 
    expert.region, 
    expert.city, 
    expert.input_date, 
    expert_grnti.rubric, 
    expert_grnti.subrubric, 
    expert_grnti.discipline, 
    grnti_classifier.description 
FROM expert 
JOIN expert_grnti ON expert.id = expert_grnti.id 
JOIN grnti_classifier ON expert_grnti.rubric = grnti_classifier.codrub 
WHERE expert.id = %d;
"""

TEMPLATE_SET_EXPERT_GRNTI = """
UPDATE expert_grnti SET rubric = %s, subrubric = %s, discipline = %s WHERE id = %d
RETURNING id, rubric, subrubric, discipline;
"""

TEMPLATE_GET_ALL_WITH_GRNTI = """
SELECT 
    expert.id, 
    expert.name, 
    expert.region, 
    expert.city, 
    expert.input_date, 
    expert_grnti.rubric, 
    expert_grnti.subrubric, 
    expert_grnti.discipline, 
    grnti_classifier.description 
FROM expert 
JOIN expert_grnti ON expert.id = expert_grnti.id 
JOIN grnti_classifier ON expert_grnti.rubric = grnti_classifier.codrub;
"""