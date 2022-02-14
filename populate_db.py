"""
This script DOES:
+ Connect to PostgreSQL database (!need to have password in file pg_password.txt)
+ Iterate through all JSON file in the data directory
+ Iterate through all articles in each JSON file
+ Compose SQL query from string to:
    + Add all articles to database (INSERT INTO pubmed22)

This script DOES NOT:
+ Create the database (run create_pmdb.sql first!)
+ Send SELECT queries to the database (for that, query_pgsql.py)
+ Print anything to screen 
    + (see the populated database in CSV format at pgsql_pubmed_data.csv)
"""


import psycopg2
import os
import json
import glob



DATA_DIR = os.path.join(os.getcwd(), "data/")
DB_NAME = "pubmed22"
TABLE_NAME = "articles"


# Connect to database and create cursor
username = "postgres"
password = open('pg_password.txt', 'r').read()
conn = psycopg2.connect(f"dbname={DB_NAME} user={username} password={password}")
cur = conn.cursor()



tot_articles_added_to_db = 0


for file in glob.iglob(f"{DATA_DIR}/*.json"):

    file_name = os.path.basename(file)

    f = open(file)
    data = json.load(f) #list

    count = 0

    for article in data:

        pmid = int(article['PMID']) #otherwise str

        title = str(article['ArticleTitle']).strip('[]') #some are 'None'
        if title == 'None':
            title = 'N/A'

        abstract = article['Abstract']
        journal = str(article['JournalTitle']).strip('[]')

        authors = article['Authors']['Author'] #list if not empty, otherwise str "N/A"
        if authors == []:
            authors = ['N/A']
        if isinstance(authors, str):
            authors = authors.split()
        authors = [x.replace("'"," ") if "'" in x else x for x in authors]
        
        
        mesh = article['SimpleMeshTerms']['MeshTerm'] #list if not empty, otherwise str "N/A"
        if isinstance(mesh, str):
            mesh = mesh.split()
        mesh = [x.replace("'"," ") if "'" in x else x for x in mesh]
        
        _year = article['PubDate']['Year']
        _month = article['PubDate']['Month']
        pub_date = f"{str(_year)}-{str(_month)}"

        query = f"INSERT INTO {TABLE_NAME} \
                (pmid, title, abstract, journal, authors, mesh, pub_date) \
                VALUES ({pmid}, $${title}$$, $${abstract}$$, $${journal}$$, \
                ARRAY{authors}, ARRAY{mesh}, $${pub_date}$$) \
                ON CONFLICT (pmid) DO NOTHING;"

        cur.execute(query)
        conn.commit()

        count += 1


    tot_articles_added_to_db += count


    print(f"+++ {count} PubMed articles from file '{file_name}' addedd to DB '{DB_NAME}' +++")

    f.close()


print(f"+++ {tot_articles_added_to_db} PubMed articles addedd to DB '{DB_NAME}' +++")
    


# Close cursor and connection to db
cur.close()
conn.close()