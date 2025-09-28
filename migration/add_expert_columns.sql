-- Добавление новых колонок в таблицу expert
-- keywords - ключевые слова
-- group_count - количество групп

ALTER TABLE expert 
ADD COLUMN keywords VARCHAR(255),
ADD COLUMN group_count INTEGER DEFAULT 0;
