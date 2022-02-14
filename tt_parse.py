"""
This script DOES:
+ Contain all functions needed to parse the extracted Medline data
    (large XML files) into more manageable formats:
        + JSON
        + reduced XML

This script DOES NOT:
+ Execute anything


Info to keep:
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


Useful links:
https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html
https://www.nlm.nih.gov/bsd/licensee/elements_alphabetical.html
https://www.nlm.nih.gov/databases/dtd/index.html

"""


import xml.etree.ElementTree as ET
import itertools
import json
import os
import datetime
from collections import OrderedDict
from dict2xml import dict2xml
from xml.dom.minidom import parseString



def get_text(article, label):
    x = article.find(label)
    # .text retrieves the text associates with a certain label
    return x.text if x is not None else ""


def parse_authors(authors):
    authors_list = []
    for author in authors:
        last_name = get_text(author, 'LastName')
        first_name = get_text(author, 'ForeName')

        if last_name != None:
            name = str(last_name)
            if first_name != None:
                name += ", " + str(first_name)
                # 2 lines below would ignore special characters
                #name = name.encode("ascii", "ignore")
                #name = name.decode()
                # For now, keep unicode encodings for special characters in names

            authors_list.append(name)

    return authors_list


def parse_mesh_terms(mesh_headings):
    # Mesh terms (i.e. headings) are contained in a list
    # Each has a descriptor name and a qualifier name (not all have both)
    # The qualifier adds some info about the descriptor
    # e.g. descriptor: covid - qualifier: diagnosis
    # means the article talks about the diagnosis of covid and not e.g. 
    # its long term consequences

    list_mesh_terms = []

    if mesh_headings != None:
        # Each heading has subelements <DescriptorName> and <QualifierName>
        for heading in mesh_headings:
            
            # 1 (findall returns a list, find returns a single element)
            descriptor_name = heading.find('DescriptorName')
            if descriptor_name != None:

                # 0 or more (usually max.2)
                # qualifier_names is always a list
                qualifier_names = heading.findall('QualifierName')
                if qualifier_names != []:

                    descriptor_qualifiers_list = []
                    descriptor = descriptor_name.text
                    descriptor_qualifiers_list.append(descriptor)

                    for q_name in qualifier_names:
                        descriptor_qualifiers_list.append(q_name.text)

                    #need this for loop if using .findall()
                    #for d_name in descriptor_names:
                        #list_mesh_terms.append(d_name.text)
                    list_mesh_terms.append(descriptor_qualifiers_list)

                else:

                    descriptor = descriptor_name.text
                    list_mesh_terms.append(descriptor)
    
    return list_mesh_terms


def parse_mesh_terms_descriptor_only(mesh_headings):

    # Mesh terms (i.e. headings) are contained in a list
    # Each has a descriptor name and a qualifier name (not all have both)
    # The qualifier adds some info about the descriptor
    # e.g. descriptor: covid - qualifier: diagnosis
    # means the article talks about the diagnosis of covid and not e.g. 
    # its long term consequences
    # Here we only keep the descriptor

    list_mesh_terms = []

    if mesh_headings != None:
        # Each heading has subelements <DescriptorName> and <QualifierName>
        for heading in mesh_headings:
            
            # 1 (findall returns a list, find returns a single element)
            descriptor_name = heading.find('DescriptorName')
            if descriptor_name != None:
                
                list_mesh_terms.append(descriptor_name.text)
    
    return list_mesh_terms


def normalise_month(month):
    month = month.replace(".", "")
    if month.isalpha():
        dt_object = datetime.datetime.strptime(month, "%b")
        month_number = dt_object.month
        #month_number = str(month_number).zfill(2)
    elif month.isdigit():
        #month_number = str(month).zfill(2)
        month_number = month
    
    #return str(month_number)
    return int(month_number)


def parse_xml_file_reduce(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    articles = itertools.chain(tree.findall('PubmedArticle'), tree.findall('BookDocument'))
    
    list_of_articles = []

    count = 0
    for article in articles:

        count += 1
        #dict_article = {}
        dict_article = OrderedDict()

        '''PubMed ID'''
        # Always one digit
        # The <PMID> is the single element to uniquely identify MEDLINE records
        PMID = get_text(article, './/PMID')
        dict_article["PMID"] = PMID
        

        '''Article title'''
        # <ArticleTitle> is always in English.
        # Those translated are enclosed in square brackets
        # Corporate/collective authors may appear at the end for articles up to year 2000
        dict_article["ArticleTitle"] = get_text(article, './/ArticleTitle')


        '''Publication date'''
        # <PubDate> contains the full date on which the issue of the journal was published. 
        # The standardized format consists of year, a 3-character abbreviated month, and day.
        # Not every record has all of these elements.

        dict_article["PubDate"] = {}
        year = get_text(article, './/JournalIssue/PubDate/Year')
        month = get_text(article, './/JournalIssue/PubDate/Month')
        
        if year != "":
            dict_article["PubDate"]["Year"] = int(year)
            if month != "":
                dict_article["PubDate"]["Month"] = normalise_month(month)
            else:
                dict_article["PubDate"]["Month"] = 00
        else:
            dict_article["PubDate"]["Year"] = 00
            dict_article["PubDate"]["Month"] = 00

            # MedlineDate is not standardised, ignore for now
            #medline_date = get_text(article, './/MedlineDate')
            #if medline_date != "":
                #dict_article["PubDate"] = medline_date
            #else:
                #dict_article["PubDate"] = 00


        '''Date revised'''
        dict_article["DateRevised"] = {}
        dict_article["DateRevised"]["Year"] = int(get_text(article, './/DateRevised/Year'))
        # Month should always be a number, but normalise to make sure
        dict_article["DateRevised"]["Month"] = int(normalise_month(get_text(
                                            article, './/DateRevised/Month')))


        '''Abstract'''
        abstract_list = article.find('.//Abstract')
        if abstract_list != None:            
            try:
                abstract = " ".join([line.text for line in abstract_list.findall('AbstractText')])
                abstract = abstract.strip(" \n")
                abstract = abstract.encode("ascii", "ignore")
                abstract = abstract.decode()
                dict_article["Abstract"] = abstract
            
            except:
                dict_article["Abstract"] = "N/A"
        else:
            dict_article["Abstract"] = "N/A"


        '''Journal title'''
        dict_article["JournalTitle"] = get_text(article, './/Journal/Title')


        '''Authors'''

        dict_article["Authors"] = {}
        # A list of elements
        all_authors = article.findall('.//Author')

        if all_authors != None:
            dict_article["Authors"]["Author"] = parse_authors(all_authors)
        else:
            dict_article["Authors"]["Author"] = "N/A"


        '''Mesh terms'''

        dict_article["SimpleMeshTerms"] = {}

        mesh_headings = article.findall('.//MeshHeading')
        list_mesh_terms = parse_mesh_terms(mesh_headings)        

        # Filters out qualifiers
        descriptor_only_list = parse_mesh_terms_descriptor_only(mesh_headings)

        if list_mesh_terms != []:
            dict_article["SimpleMeshTerms"]["MeshTerm"] = descriptor_only_list

        else:
            dict_article["SimpleMeshTerms"]["MeshTerm"] = "N/A"

        list_of_articles.append(dict_article)
    
    print(f"+++ {count} PubMed articles parsed +++")
    #print("No mesh terms found for %d articles" %len(no_mesh_terms_found))
    #print("Mesh terms found for %d articles" %(count - len(no_mesh_terms_found)))
    
    return list_of_articles


def create_reduced_xml(original_file, parsed_file, out_filename):
    original_filename = os.path.basename(original_file)
    original_dir = os.path.dirname(original_file) #data/

    # parsed_file is a list of dictionaries
    # Create XML string from the list of parsed articles
    xml = dict2xml(parsed_file, wrap ='PubmedArticle', indent ="    ")

    # Add declaration and root element
    output_xml = "<?xml version='1.0' encoding='utf-8'?>\n<PubmedArticleSet>\n" + xml + "\n</PubmedArticleSet>"

    # Write new (reduced) XML file
    out_path = os.path.join(original_dir, out_filename)
    out_file = open(out_path, 'w')
    out_file.write(output_xml)
    print(f"+++ Created reduced version of XML file {original_filename} +++")
    out_file.close()



def create_json(original_file, parsed_file, out_filename):
    original_filename = os.path.basename(original_file)
    original_dir = os.path.dirname(original_file) #data/

    out_path = os.path.join(original_dir, out_filename)
    out_file =  open(out_path, "w")
    json.dump(parsed_file, out_file, indent=6)
    print(f"+++ Created JSON version of XML file {original_filename} +++")
    out_file.close()
    