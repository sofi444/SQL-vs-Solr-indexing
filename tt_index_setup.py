"""
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

"""


import subprocess as sp



''' Set Solr directory (/bin) '''
# My local machine
SOLR_BIN_DIR = "/Users/sofy/Documents/Workspace/Apps/solr-8.11.0/bin"


''' Set name of index, hostname and port to be used '''
core_name = "pubmed_index"
confingset = "myconfigs_pm"

# Insert name of server or IP if running on a server e.g. "phoenix.ims.uni-stuttgart.de"
# If running on local -> localhost
hostname = "localhost" 

port = "8983" # Solr default port



''' Check if Solr is running'''
solr_status = sp.Popen("./solr status", shell=True, cwd=SOLR_BIN_DIR)
solr_status.wait()
 
# If Solr is alreary running the return code will be 0
if solr_status.returncode != 0:

    ''' Start Solr '''
    start = sp.Popen(f"./solr start -p {port}", shell=True, cwd=SOLR_BIN_DIR)
    start.wait()
    if start.returncode == 0:
        print("+++ Started SOLR +++")

elif solr_status.returncode == 0:
    print("+++ Solr is running +++")



''' Check if core already exists '''
check_core = sp.Popen(f"curl -sI {hostname}:{port}/api/cores/{core_name} \
            | grep 'HTTP/1.1 200 OK'", shell=True, cwd=SOLR_BIN_DIR)
check_core.wait()

# If core does not exist, create it
if check_core.returncode != 0:

    ''' Create Solr core '''
    create = sp.Popen(f"./solr create_core -c {core_name} -d {confingset} -V", 
                        shell=True, cwd=SOLR_BIN_DIR)
    create.wait()

    if create.returncode == 0:
        print(f"+++ Successfully created index '{core_name}' +++")

if check_core.returncode == 0:
    print(f"+++ Index '{core_name}' exists +++")

