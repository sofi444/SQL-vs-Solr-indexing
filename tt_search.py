"""
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

"""


from urllib.request import urlopen
import urllib.parse
import configparser
import json
import time
import pprint



config = configparser.ConfigParser()
config.read('config.ini')


def config_value(parameter, config):
    config.read('config.ini')

    if config['MANUAL'][parameter] != 'None':
        value = config['MANUAL'][parameter]
    else:
        value = config['DEFAULT'][parameter]
    return value



core_name = config['CORE']['core_name']
hostname = config['CORE']['hostname']
port = config['CORE']['port']



solr_parameters = [
    ('q', f"{config_value('query', config)}"),
    ('fq', f"{config_value('filter_query', config)}"),
    ('fq', f"{config_value('filter_query2', config)}"),
    ('q.op', f"{config_value('query_operator', config)}"),
    ('rows', f"{config_value('num_displayed_results', config)}"),
    ('start', f"{config_value('display_from_num', config)}"),
    ('sort', f"{config_value('sort_by', config)}"),
    ('fl', f"{config_value('returned_fields', config)}"),
    ('defType', f"{config_value('parser', config)}"),
    ('qf', f"{config_value('fields_to_query', config)}"),
    ('df', f"{config_value('default_field', config)}"),
    ('wt', f"{config_value('response_format', config)}"),
    ('indent', f"{config_value('indent', config)}"),
    ('debug', f"{config_value('debug', config)}")
]


solr_url = f"http://{hostname}:{port}/solr/{core_name}/select?"
# Encode parameters in URL format
encoded_solr_parameters = urllib.parse.urlencode(solr_parameters, safe='()', quote_via=urllib.parse.quote)

complete_url = solr_url + encoded_solr_parameters
print(complete_url)

# Run query
start = time.time()
connection = urlopen(complete_url)
end = time.time()

raw_response = json.load(connection)

time_taken_sec = round(end-start, 5)
time_taken_ms = round((end-start)*1000, 5)

pp = pprint.PrettyPrinter(indent=4, width=130)
pp.pprint(raw_response) #type dict
print(f"+++ Time taken (connection + query processing): {time_taken_sec} seconds \n or {time_taken_ms} ms [SOLR] +++")