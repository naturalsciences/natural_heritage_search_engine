import pandas as pd
import numpy as np
import requests,json
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import re
import sys

es=None
cols_obj={}
dict={}
dict_inst={}
results={}
src_excel="cetaf_user_as_excel_full.xlsx"

INDEX_NAME_EXPERTISES="cetaf_passport_expertises"


def parse_row(row_excel, row_json, key_excel, key_json):
    row_json[key_json]=None
    if key_excel in row_excel:
        row_json[key_json]=str(row_excel[key_excel]).strip().replace("\r\n", "<br/>")
        print(key_json)
        print(row_json[key_json])
        
    return row_json
        
def parse_for_es():
    global es
    global INDEX_NAME_EXPERTISES
    global results
    pattern = re.compile('\d+\s*\.\s*\d*')
    i=0
    for key, item in results.items():
     
        row_json={}
        
        row_json=parse_row(item, row_json, "email", "email")
        row_json=parse_row(item, row_json, "expertise", "expertise")
        row_json=parse_row(item, row_json, "institution", "institution")
        row_json=parse_row(item, row_json, "service", "service")
        row_json=parse_row(item, row_json, "first_name", "first_name")
        row_json=parse_row(item, row_json, "last_name", "last_name")
        row_json=parse_row(item, row_json, "country", "country")
        row_json=parse_row(item, row_json, "mars_code", "mars_code")
        name_full=""
        if row_json["first_name"] is not None:
            name_full=row_json["first_name"]
        if row_json["last_name"] is not None:
            name_full=name_full+ " "+row_json["last_name"]
        name_full=name_full.strip()
        expertise=None
        if  row_json["expertise"] is not np.nan:
            expertise=[str(row_json["expertise"]).strip()] 
            print("Expertise =")
            print(expertise)
        print(name_full)
        
        updated= {
                   
                   "person":{
                            "email":row_json["email"],
                            "name":name_full,
                            "type":str(row_json["service"]).strip(),
                            "person_description":expertise                           
                    },
                     "to_parent_collection_in_institution" :[{
                        "institution_name":str(row_json["institution"]).strip(),
                        "institution_acronym":str(row_json["mars_code"]).strip(),
                         "collection_name":str(row_json["service"]).strip()
                    }],
                    "areas_of_expertise": expertise,
                    "country_en":str(row_json["country"]).strip(),
                    "to_parent_institution":str(row_json["mars_code"]).strip(),
                        
                    
                 }
        
        response2 = es.update(index=INDEX_NAME_EXPERTISES,  id=str(i), body={"doc":updated,'doc_as_upsert':True})
        print(response2)
        i=i+1
        

def parse(excel):
    global results
    print(excel)
    ex_data = pd.read_excel(excel)
    headers=ex_data.head()
    current_inst=""
    i=0
    for cols in ex_data.columns:
        print(cols)
        cols_obj.update({i:cols})
        i+=1
    iData=0
    for i, row in ex_data.iterrows():
        if not row[1] is np.nan:
            print(i)
            key_facility=row[1]
            print(key_facility)
            json_row={}
            for key, col_name in cols_obj.items():
                json_row[col_name] =row[key]
            print(json_row)
            results[key_facility] = json_row
            iData+=1
            print(iData)            

if __name__ == "__main__":
    es =  Elasticsearch(
        ['ursidae.rbins.be'],       
        use_ssl = False,
        port=9200,
    )
    parse(src_excel)
    parse_for_es()

