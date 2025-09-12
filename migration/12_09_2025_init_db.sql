CREATE TABLE expert (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50),
    region      VARCHAR(50),
    city        VARCHAR(50),
    input_date  DATE
);

CREATE TABLE expert_grnti (
    id          INTEGER REFERENCES expert (id) ON DELETE CASCADE,
    rubric      SMALLINT NOT NULL,
    subrubric   SMALLINT,
    siscipline  SMALLINT
);

CREATE TABLE grnti_classifier (
    codrub      SMALLINT UNIQUE,
    description VARCHAR(100)
);

CREATE TABLE reg_obl_city (
    region  VARCHAR(100),
    oblname VARCHAR(100),
    city    VARCHAR(100)
);
