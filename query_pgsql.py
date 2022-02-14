"""
This script DOES:
+ Connect to existing database (!need to have password in file pg_password.txt)
+ Compose a series of queries as strings
+ Iterate through queries, run + time them
+ Print time taken to run queries for following analysis

This script DOES NOT:
+ Create the database (run create_pmdb.sql first!)
+ Populate the database (run populate_db.py first!)

Useful links:

https://www.postgresql.org/docs/9.5/textsearch-tables.html
https://www.postgresql.org/docs/current/textsearch-controls.html
https://www.sqlshack.com/sql-index-overview-and-strategy/ (how it works internally)
https://www.compose.com/articles/mastering-postgresql-tools-full-text-search-and-phrase-search/

"""


import psycopg2
import time
import pprint


DB_NAME = "pubmed22"
TABLE_NAME = "articles"


# Connect to database and create cursor
username = "postgres"
password = open('pg_password.txt', 'r').read()
conn = psycopg2.connect(f"dbname={DB_NAME} user={username} password={password}")
cur = conn.cursor()


# tsquery operators & (AND), | (OR), ! (NOT), and <#> (proximity)


# NoIdx Gender
q1 = f"SELECT title,abstract,pub_date FROM {TABLE_NAME} \
            WHERE position('gender' in abstract) > 0 AND \
            position('identity' in abstract) > 0 AND \
            position('education' in abstract) > 0 \
            ORDER BY pub_date DESC \
            LIMIT 3;"

# NoIdx ADHD
q2 = f"SELECT title,abstract,pub_date FROM {TABLE_NAME} \
            WHERE position('ADHD' in abstract) > 0 AND \
            position('children' in abstract) > 0 \
            ORDER BY pub_date DESC \
            LIMIT 3;"

# NoIdx VaxReaction
q3 = f"SELECT title,abstract,pub_date FROM {TABLE_NAME} \
            WHERE (position('covid' in abstract) > 0 OR \
                position('coronavirus' in abstract) > 0) AND \
            position('vaccine' in abstract) > 0 AND \
            position('reaction' in abstract) > 0 \
            LIMIT 3;"

# vectorise on the fly, slower
# Idx VaxReaction OTF
q4 = f"SELECT title,abstract,pub_date,ts_rank_cd(vector, query) AS rank  \
            FROM {TABLE_NAME}, \
                to_tsquery( '(coronavirus|covid) & vaccine & reaction' ) AS query \
            WHERE to_tsvector(title || ' ' || abstract) @@ query \
            ORDER BY rank DESC \
            LIMIT 3;"

# Idx VaxReaction
q5 = f"SELECT title,abstract,pub_date,ts_rank_cd(vector, query) AS rank \
            FROM {TABLE_NAME}, \
                to_tsquery( '(coronavirus|covid) & vaccine & reaction' ) AS query \
            WHERE vector @@ query \
            ORDER BY rank DESC \
            LIMIT 3;"

# Idx VaxSmoking
q6 = f"SELECT title,abstract,pub_date,ts_rank_cd(vector, query) AS rank \
            FROM {TABLE_NAME}, \
                to_tsquery( '(coronavirus|covid) & vaccine & smoking' ) AS query \
            WHERE vector @@ query \
            ORDER BY rank DESC \
            LIMIT 3;"

# Idx Gender
q7 = f"SELECT title,abstract,pub_date,ts_rank_cd(vector, query) AS rank \
            FROM {TABLE_NAME}, \
                to_tsquery( 'gender & identity & education' ) AS query \
            WHERE vector @@ query \
            ORDER BY rank DESC \
            LIMIT 3;"

# Idx ADHD
q8 = f"SELECT title,abstract,pub_date,ts_rank_cd(vector, query) AS rank \
            FROM {TABLE_NAME}, \
                to_tsquery( 'ADHD & children' ) AS query \
            WHERE vector @@ query \
            ORDER BY rank DESC \
            LIMIT 3;"

# Idx AnxietyProximity
q9 = f"SELECT title,abstract,pub_date,ts_rank_cd(vector, query) AS rank \
            FROM {TABLE_NAME}, \
                to_tsquery( 'anxiety <-> in <-> women' ) AS query \
            WHERE vector @@ query \
            ORDER BY rank DESC \
            LIMIT 3;"

# Idx MentalHealth
q10 = f"SELECT title,abstract,pub_date,ts_rank_cd(vector, query) AS rank \
            FROM {TABLE_NAME}, \
                to_tsquery( '(mental <-> health) & covid & students' ) AS query \
            WHERE vector @@ query \
            ORDER BY rank DESC \
            LIMIT 3;"




queries = {'#1 NoIdx Gender': q1,
            '#2 NoIdx ADHD': q2,
            '#3 NoIdx VaxReaction': q3,
            '#4 Idx VaxReaction OTF': q4,
            '#5 Idx VaxReaction': q5,
            '#6 Idx VaxSmoking': q6,
            '#7 Idx Gender': q7,
            '#8 Idx ADHD': q8,
            '#9 Idx AnxietyProximity': q9,
            '#10 Idx MentalHealth': q10
            }



# Execute queries
total_time_for_queries_sec = 0

idx = 0

for query_name, query in queries.items():
    start = time.time()
    cur.execute(query)
    end = time.time()
    conn.commit()

    time_taken_sec = end-start
    time_taken_ms = (end-start)*1000

    total_time_for_queries_sec += time_taken_sec
    idx += 1

    results = cur.fetchall()

    print(f"=========================================================== \
            \n{query_name}: {query}")
    print(f"\n+++ Query #{idx} processing time: \
            {round(time_taken_sec, 5)} seconds \n or \
            {round(time_taken_ms, 5)} ms [SQL] +++")
    print(f"+++ Retrieved results for query #{idx}: {len(results)} +++")

    pp = pprint.PrettyPrinter(indent=4, width=130)
    pp.pprint(results)

total_time_for_queries_ms = total_time_for_queries_sec*1000

print(f"\n\n+++ Processing time for all 6 (index) queries (#5-#10): \
        {total_time_for_queries_sec} seconds \n or \
        {total_time_for_queries_ms} ms [SQL] +++")



# Close cursor and connection to db
cur.close()
conn.close()
