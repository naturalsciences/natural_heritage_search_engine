import pandas as pd
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
src_excel="passport_export_facilities_flat_mod.xlsx"

INDEX_NAME_FACILITIES="cetaf_passport_facilities"


def parse_row(row_excel, row_json, key_excel, key_json):
    row_json[key_json]=None
    if key_excel in row_excel:
        row_json[key_json]=str(row_excel[key_excel]).strip().replace("\r\n", "<br/>")
        print(key_json)
        print(row_json[key_json])
        
    return row_json
        
def parse_for_es():
    global es
    global INDEX_NAME_FACILITIES
    global results
    pattern = re.compile('\d+\s*\.\s*\d*')
    for key, item in results.items():
        key_inst=item["mars_code"]
        print(key_inst)
        row_json={}
        if "laboratory" in item:
            item["laboratory"]= pattern.sub('', item["laboratory"])
        row_json=parse_row(item, row_json, "mars_code", "mars_code")
        row_json=parse_row(item, row_json, "country", "country")
        row_json=parse_row(item, row_json, "institution", "institution")
        row_json=parse_row(item, row_json, "laboratory", "laboratory")
        row_json=parse_row(item, row_json, "laboratory_desc", "laboratory_desc")
        row_json=parse_row(item, row_json, "tools", "tools")
        print(row_json)
        print(row_json["laboratory"])
        facility_key=key_inst+"/"+row_json["laboratory"]
        updated= {
                   
                    "facility_acronym":facility_key,
                    "facility_type":row_json["laboratory"],
                    "laboratories":row_json["laboratory"],
                    "facility_name":row_json["laboratory"],
                    "facility_description":row_json["laboratory_desc"],
                    "institution_name":row_json["institution"],
                    "available_tools":{"tool_description":row_json["tools"]},
                    "facility_address":{"country": row_json["country"]},
                    "to_parent_institution": key_inst
                 }
        
        response2 = es.update(index=INDEX_NAME_FACILITIES,  id=facility_key, body={"doc":updated,'doc_as_upsert':True})
        

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
    for i, row in ex_data.iterrows():
        print(i)
        key_facility=row[1]+"/"+row[3]
        print(key_facility)
        json_row={}
        for key, col_name in cols_obj.items():
            json_row[col_name] =row[key]
        print(json_row)
        results[key_facility] = json_row       

if __name__ == "__main__":
    es =  Elasticsearch(
        ['ursidae.rbins.be'],       
        use_ssl = False,
        port=9200,
    )
    parse(src_excel)
    parse_for_es()

