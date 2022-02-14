"""
This script DOES:
+ Contain a series of Solr queries
+ Iterate through the queries and run them one by one (by calling the file tt_search.py)
+ Update config.ini on the fly to set query params

"""

import configparser
import subprocess as sp


config = configparser.ConfigParser()

def write_query_to_config(query, config):
    config.read('config.ini')
    config.set('MANUAL', 'query', query)

    with open('config.ini', 'w') as configfile:
        config.write(configfile)



queries = {'Solr VaxReaction': '(coronavirus OR covid) AND vaccine AND reaction',
            'Solr VaxSmoking': '(coronavirus OR covid) AND vaccine AND smoking',
            'Solr Gender': 'gender AND identity AND education',
            'Solr ADHD': 'ADHD AND children',
            'Solr AnxietyProximity': '\"anxiety in women\"',
            'Solr MentalHealth': '\"mental health\" AND covid AND students'
            }



for query_name, query in queries.items():
    write_query_to_config(query, config)
    sp.run('python3 tt_search.py', shell=True, check=True)
