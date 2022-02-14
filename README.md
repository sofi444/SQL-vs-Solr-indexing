# TT-index-pubmed
  Indexing of Medline/Pubmed data with Solr and SQL


## Requirements
  + SOLR has to be installed (I used version 8.11.0)
      https://solr.apache.org/guide/8_11/installing-solr.html
  + PostgreSQL has to be installed (I used version 14 for Mac)
      https://www.postgresql.org/download/
  + Install necessary Python libraries by running: pip install -r requirements.txt
  + Write password for postgreSQL in file pg_password.txt
  + Python (I used version 3.10)


## The Data

  The data used for this project are 5 files from the 2022 release of the Medline baseline.

  Data source:
  + https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/
  + https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/README.txt

  The data was downloaded manually from the source.
  The full baseline (1114 files) can be downloaded by command: \
    f"wget -q -r --directory-prefix={DATA_DIR} --no-parent ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/"


  ### tt_data.py

  This script DOES:
  + Check integrity of downloaded data (md5 checksum)
  + Extract zipped data to the data directory
  + Check successful extraction
  + Iterate through all XML files
  + Call parsing function from the file tt_parse.py
      + Extract from large XML files only needed info
  + (optionally) Delete .gz and .xml files to free up space
  + Output parsed data in two formats:
      + (reduced) XML
      + JSON

  This script DOES NOT:
  + Download the data from source


  ### tt_parse.py

  This script DOES:
  + Contain all functions needed to parse the extracted Medline data
      (large XML files) into more manageable formats:
          + JSON
          + reduced XML

  This script DOES NOT:
  + Execute anything

  Info to keep from original Pubmed data:
  + PMID
  + Title of paper
  + Publication Date
  + Revision Date (<DateRevised> resides on all records at time of export. 
      It identifies the date a change is made to a record. May be useful
      to know which docs to update after new baseline download (yearly)
  + Abstract
  + Authors
  + Name of journal
  + Mesh terms (full + simple)

  Useful links: \
  https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html \
  https://www.nlm.nih.gov/bsd/licensee/elements_alphabetical.html \
  https://www.nlm.nih.gov/databases/dtd/index.html
  

  
## SOLR

  Files should be run in this order: tt_index_setup.py, tt_index_pubmed.py, tt_search.py/tt_all_solr_queries.py
  
  
  ### schema.xml
  
  The personalised schema that Solr will use for the index.
  It tells Solr what data will be index, what data types and generally how to handle the data.
  
  !! This file should be inside the myconfigs_pm/conf/ folder. To create myconfigs_pm folder copy the _default folder at 'solr-8.11.0/server/solr/configsets/_default' in the same directory, rename myconfigs_pm and move schema.xml into it.
  
  
  ### tt_index_setup.py
  
  This script DOES:
  + Start Solr (!Solr has to exist on machine)
  + Create core (ie. index) if it does not exist already
      + Use customised config set: myconfigs_pm
          which is a directory inside ../server/solr/configsets/
          -> This prevents Solr from using the _default configsets
          with a default schema.
          -> Solr will still create a managed-schema file automatically,
              from the schema.xml in myconfigs_pm so that it can later
              be modified through the API (if needed)

  This script DOES NOT:
  + Install Solr
  + Populate Solr index (for that, run tt_index_pubmed.py)

  !! Before running DO:
  + Make sure Solr is installed
  + Adjust the setting at the beginning of the script:
      + Set Solr directory (bin directory inside installation folder)
      + Choose name of core
      + Set Solr host and port
  
  
  ### tt_index_pubmed.py
  
  This script DOES:
  + Call tt_index_setup.py file, which
      + Starts Solr
      + Creates core
  + Feed all json file in the data directory to the Solr index
  + Check successful posting

  This script DOES NOT:
  + Install Solr (!has to be installed)
  
  
  ### tt_search.py
  
  This script DOES:
  + Read config.ini file, where the query params are specified
  + Transform the user specified (human-readable) query params
      into 'Solr format/language'
  + Compose a URL from the query params
  + Runs query via URL
  + Print Solr response
  + Time queries for following analysis

  This script DOES NOT:
  + Install Solr
  + Start Solr
  + Creates core

  Before running DO:
  + Make sure Solr is installed
  + Make sure Solr core exists and is populated with data
      (files tt_index_setup.py and tt_index_pubmed.py)
  
  
  ### config.ini
  
  This file is used for modifying the query parameters, which are presented in a more readable way.
  It is used with the Python library ConfigParser. The parameters are read from this file and used for creating a Solr query
  
  
  ### tt_all_solr_queries.py
 
  This script DOES:
  + Contain a series of Solr queries
  + Iterate through the queries and run them one by one (by calling the file tt_search.py)
  + Update config.ini on the fly to set query params
  
  
  ### solr_output_terminal.rtf
  
  It contains the output produced when running the file tt_all_solr_queries.py \
  Only 3 results per query are printed out.
  
  
## SQL
  
  ### create_pmdb.sql
  
  This script creates a database 'pubmed22' with one table 'articles' which contains ~130.000 rows. The entries are biomedical articles from the Medline 2022 baseline corpus.
  
  This script DOES NOT populate the database with data (for that, populate_db.py)
  
  
  ### populate_db.py
  
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
  
  
  ### pgsql_pubmed_data_reduced.csv
  
  (a sample of) The PostgreSQL database (in CSV format) after being filled with data.
  
  
  ### query_pgsql.py
  
  This script DOES:
  + Connect to existing database (!need to have password in file pg_password.txt)
  + Compose a series of queries as strings
  + Iterate through queries, run + time them
  + Print time taken to run queries for following analysis

  This script DOES NOT:
  + Create the database (run create_pmdb.sql first!)
  + Populate the database (run populate_db.py first!)

  Useful links:

  https://www.postgresql.org/docs/9.5/textsearch-tables.html \
  https://www.postgresql.org/docs/current/textsearch-controls.html \
  https://www.sqlshack.com/sql-index-overview-and-strategy/ (how it works internally) \
  https://www.compose.com/articles/mastering-postgresql-tools-full-text-search-and-phrase-search/
  
  
  ### sql_output_terminal.rtf
  
  It contains the output produced when running the file query_pgsql.py \
  Only 3 results per query are printed out.
