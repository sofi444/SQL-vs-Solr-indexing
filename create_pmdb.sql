-- This script DOES:
---- create a database 'pubmed22' with one table 'articles'
------ which contains ~130.000 rows. The entries are biomedical
------ articles from the Medline 2022 baseline corpus.

-- This script DOES NOT:
---- Populate the database with data (for that, populate_db.py)



-- Database: pubmed22

DROP DATABASE IF EXISTS pubmed22;

CREATE DATABASE pubmed22
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;


\connect pubmed22



-- Table: public.articles

DROP TABLE IF EXISTS public.articles;

CREATE TABLE IF NOT EXISTS public.articles
(
    pmid integer NOT NULL,
    title text COLLATE pg_catalog."default",
    abstract text COLLATE pg_catalog."default",
    journal text COLLATE pg_catalog."default",
    authors text[] COLLATE pg_catalog."default",
    mesh text[] COLLATE pg_catalog."default",
    pub_date character varying(7) COLLATE pg_catalog."default",
    vector tsvector,
    CONSTRAINT pubmed_pkey PRIMARY KEY (pmid)
)


TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.articles
    OWNER to postgres;



-- Delete 'N/A' otherwise it will be counted a word when vectorising
UPDATE public.articles
    SET mesh = {''}
    WHERE mesh = {'N/A'};

UPDATE public.articles
    SET title = {''}
    WHERE title = {'N/A'};

UPDATE public.articles
    SET abstract = {''}
    WHERE abstract = {'N/A'};



-- Vectorise title and abstract
-- Store in new column 'vector'
ALTER TABLE public.articles
    ADD COLUMN vector tsvector;
UPDATE public.articles
    SET vector = to_tsvector('english', coalesce(title,'') || ' ' || coalesce(abstract,''));



-- Create index on column 'vector'
-- Index: vec_index

DROP INDEX IF EXISTS public.vec_index;

CREATE INDEX IF NOT EXISTS vec_index
    ON public.articles USING gin
    (vector)
    TABLESPACE pg_default;