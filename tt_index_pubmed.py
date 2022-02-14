"""
This script DOES:
+ Call tt_index_setup.py file, which
    + Starts Solr
    + Creates core
+ Feed all json file in the data directory to the Solr index
+ Check successful posting

This script DOES NOT:
+ Install Solr (!has to be installed)

"""


'''Required Imports'''

import glob
import os
import subprocess as sp
from tt_index_setup import SOLR_BIN_DIR, core_name, hostname, port


'''Set Directories'''

CW_DIR = os.getcwd() #text_tech/
DATA_DIR = os.path.join(CW_DIR, 'data/')


'''Pipeline'''
idx = 0

error_indexing_files = []
number_of_files = len(glob.glob(f"{DATA_DIR}/*.json"))



# Iterate through json files in data dir
# iglob returns an iterator object (json files with full path)
for json_path in glob.iglob(f"{DATA_DIR}/*.json"):

    json_filename = os.path.basename(json_path)

    '''Post to Index'''
    post = sp.Popen(f"./post -c {core_name} {json_path}", shell=True, cwd=SOLR_BIN_DIR)
    post.wait()
    
    if post.returncode != 0:
        print(f"!!! There was an error in indexing file '{json_filename}' !!!")
        error_indexing_files.append(json_filename)

    elif post.returncode == 0:
        print(f"+++ Successful indexing of file '{json_filename}' +++")
        
        idx += 1



print(f"-> {idx}/{number_of_files} files processed")
print(f"-> {len(error_indexing_files)} files not indexed")