"""
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
    Data can be found at the link below.
    Download a few files manually or all (mind the size!)
    by command:
        f"wget -q -r --directory-prefix={DATA_DIR} --no-parent \
            ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/")

Data source:
https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/
https://ftp.ncbi.nlm.nih.gov/pubmed/baseline/README.txt

"""


import os
import re 
import subprocess as sp
import tt_parse as parse



''' Set data directory here '''

# Local location of this file: /Users/sofy/Desktop/StuttgartUni/text_tech/ (CWD)
DATA_DIR = os.path.join(os.getcwd(), "data/")




##### Md5-checksum #####

def check_all_md5_in_dir(dir):

    # Verify the integrity of the file download
    # Check that md5 files exist
    if os.system("which md5sum 1>/dev/null") != 0:
        print("md5sum not found")
        return

    count = 0
    print(f"+++ Start checking md5 in {dir} +++")
    print("I am verifying the integrity of the downloaded files...")
    if os.path.isdir(dir):
        for file in os.listdir(dir):
            if re.search('^pubmed22n\d\d\d\d.xml.gz$', file):
                count += 1
                check_md5(os.path.join(dir, file))
                if count % 100 == 0:
                    print(f"{count} files checked")
        print(f"+++ All md5 checks succeeded ({count} files) +++")

    else:
        print(f"Directory not found: {dir} (for md5 check)")


def check_md5(file):

    if os.path.isfile(file) and os.path.isfile(file + ".md5"):

        # "md5sum" on Linux; "md5" on Mac
        stdout = sp.check_output(f"md5 {file}", \
                                shell=True).decode('utf-8')

        md5_calculated = re.search('[0-9a-f]{32}', stdout).group(0)
        md5 = re.search('[0-9a-f]{32}', open(file + ".md5",\
                                    'r').readline()).group(0)

        if md5 != md5_calculated:
            print(f"Error: md5 check failed for file {file}")
            # Abnormal exit
            exit(1)



##### Data extraction #####
#Downloaded data files are in a compressed .gz format, which need to be
#extracted. ('gunzip -fqk')

def extract(file):
    extract_rc = os.system(f"gunzip -fqk {file}")
    if extract_rc != 0:
        print(f"Error: gunzip return code for file {file} is {extract_rc}")
        exit(extract_rc)
    return extract_rc


def extract_all_gz_in_dir(dir):
    if os.path.isdir(dir):
        count = 0
        print(f"\n+++ Start extracting in {dir} +++")

        for file in os.listdir(dir):
            if re.search('.*\.gz$', file):
                extract(os.path.join(dir, file))
                count += 1
        
        if check_successful_extraction:
            print(f"+++ All files successfully extracted ({count} files). +++")
    
    else:
        print(f"Directory not found: {dir} (for extraction)")


def check_successful_extraction(dir):
    # Count files
    num_gz_files = 0
    num_xml_files = 0
    for file in os.listdir(dir):
        if file.endswith(".gz"):
            num_gz_files += 1
        elif file.endswith(".xml"):
            num_xml_files += 1
    
    if num_xml_files == num_gz_files:
        print("+++ Successful extraction of all gz files in this directory +++")
        return True
    else:
        print("!!! Warning: the number of XML files does not match the \
            number of compressed files !!!")
        return False



##### XML Parsing + Output #####

def extract_parse_output(DIR):

    # dir will contain a .gz and a .xml file for each filename
    extract_all_gz_in_dir(DIR)

    if check_successful_extraction(DIR) == True:
        
        for file in os.listdir(DIR):

            if file.endswith(".xml"):

                xml_path = os.path.join(DIR, file)

                '''Parse'''
                parsed_file = parse.parse_xml_file_reduce(xml_path)
                print("+++ Done parsing XML file +++")
                
                '''Delete .gz and .xml files to free up space'''
                #print(f"+++ Deleting original XML file {file} +++")
                #os.remove(xml_path)

                #gz_filename = file + ".gz"
                #gz_path = os.path.join(DIR, gz_filename)
                #print(f"+++ Deleting compressed (.gz) file {gz_filename} +++")
                #os.remove(gz_path)

                '''Create reduced XML'''
                reduced_xml_filename = "reduced_" + file
                parse.create_reduced_xml(xml_path, parsed_file, reduced_xml_filename)

                '''Create JSON'''
                json_filename = file + ".json"
                parse.create_json(xml_path, parsed_file, json_filename)









##### Run the pipeline #####

'''MD5 Checksum'''
# Verify the integrity of dowloaded files
check_all_md5_in_dir(DATA_DIR)

'''Extraction'''
# Extract all files in the directory
extract_all_gz_in_dir(DATA_DIR)

'''Parse + Output (JSON + reduced XML)'''
extract_parse_output(DATA_DIR)