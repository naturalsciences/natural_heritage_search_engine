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
src_excel="C:\\Users\\ftheeten\\Downloads\\CETAF_institutions_GrSciColl_Mars_code.xlsx"

INDEX_NAME_INSTITUTIONS="cetaf_passport_institutions"
INDEX_NAME_INSTITUTIONS_FULL="cetaf_passport_institutions_full"

def parse_for_es():
    global es
    global INDEX_NAME_INSTITUTIONS_FULL
    global results
    for key, item in results.items():
        key_inst=item["mars_code"]
        updated={}
        updated2={}
        print(key)
        print(item)
        #repr=item["Name official representative"]
        #url=item["Website_url"]
        print(repr)
        desc=[]
        if "Type of institution" in item:
            desc.append(item["Type of institution"])
        if "Other" in item:
            desc.append(item["Other"])
        if "Specify" in item:
            desc.append("Part of "+item["Specify"])
        updated["institution_description"]='<br/>'.join(desc)
        
        director_or_legal_representative={}
        if "rep_name" in item:
            director_or_legal_representative["dir_rep_name"]=item["rep_name"]
        if "rep_title" in item:
            director_or_legal_representative["dir_rep_description"]=item["rep_title"]
        if "rep_phone" in item:
            director_or_legal_representative["dir_rep_phone"]=item["rep_phone"]
        if "rep_mail" in item:
            director_or_legal_representative["dir_rep_email"]=item["rep_mail"]
        updated["director_or_legal_representative"]=director_or_legal_representative
        updated2["director_or_legal_representative"]=updated["director_or_legal_representative"]
        
        updated["identification_fields"]={}
        if "original_name" in item and "lang" in item:
            updated["identification_fields"]["original_name"]=[{"lang":item["lang"],"iso639":item["lang"], "translated_name":item["original_name"]}]
        else:
            updated["identification_fields"]["original_name"]=[]
            
        updated["institution_address"]={}
        updated2["institution_address"]={}
        if "email" in item:
            updated["institution_address"]["email"]=item["email"]
            updated2["institution_address"]["email"]=updated["institution_address"]["email"]
        else:
            updated["institution_address"]["email"]=[]
            updated2["institution_address"]["email"]=[]
            
        updated["organisation"]={}
        updated2["research"]={} 
        if "Legal reference" in item:
            updated["organisation"]["organisation_description"]=item["Legal reference"]
        else:
            updated["organisation"]["organisation_description"]=[]
        if "Name Cetaf Deputy" in item:
            updated["organisation"]["direction_governing_and_executive_bodies"]=item["Name Cetaf Deputy"].replace("\r\n", "<br/>")
        else:
            updated["organisation"]["direction_governing_and_executive_bodies"]=[]
        if "Name other staff members" in item:
            updated["organisation"]["staff_fields"]=item["Name other staff members"].replace("\r\n", "<br/>")
        else:
            updated["organisation"]["staff_fields"]=[]
        
        
        updated["research"]={}
        res=[]        
        if "research_general" in item:
            updated["research"]["general_description"]=item["research_general"]
        else:
            updated["research"]["general_description"]=[]
        if "research_fields" in item:
            res=re.split(';|,|\\|and|\.|\:',item["research_fields"].replace("(","").replace(")",""))
            res=[item.strip() for item in res]
            res=[item for item in res if len(item) > 2  ]
            print(res)
            updated["research"]["research_fields"]=sorted(res, key=str.lower)
            res=[item.capitalize() for item in res]
            updated2["research"]["research_fields"]=sorted(res, key=str.lower)
        else:
            updated["research"]["research_fields"]=[]
            updated2["research"]["research_fields"]=[]
        
        response2 = es.update(index=INDEX_NAME_INSTITUTIONS_FULL,  id=key_inst, body={"doc":updated})
        
        
        
        response2 = es.update(index=INDEX_NAME_INSTITUTIONS,  id=key_inst, body={"doc":updated2})
           
def add_or_concatenate_key(row, institution, pos, field):
    global results
    if not pd.isna(row[pos]):
        existing=""
        if field in results[institution]:            
            existing=results[institution][field]
            print("EXISTING "+field + " in "+institution+"="+existing)
            existing=existing+"\r\n"+str(row[pos])
        else:
            print("NEW "+field + " in "+institution+"="+str(row[pos]))
            existing=str(row[pos])
        results[institution].update({field:str(existing).strip()})

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
        if not pd.isna(row[0]):
            current_inst=row[1].lower() #mars_code
            results.update({current_inst:{}})
        print(current_inst)
        
        results[current_inst].update({'name':current_inst})
        for key, col_name in cols_obj.items():
              print(key)
              print(col_name)
              print(row[key])
              add_or_concatenate_key(row, current_inst, key, col_name)
    print(results)

            
if __name__ == "__main__":
    es =  Elasticsearch(
        ['ursidae.rbins.be'],       
        use_ssl = False,
        port=9200,
    )
    parse(src_excel)
    parse_for_es()
