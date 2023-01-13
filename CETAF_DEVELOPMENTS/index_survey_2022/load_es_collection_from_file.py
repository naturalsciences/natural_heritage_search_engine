import argparse
import requests
from requests.auth import HTTPBasicAuth
import json
from elasticsearch import Elasticsearch
import pandas as pnd

es=None
csv_collection_geo="C:\\DEV\\CETAF\\collections_geographic.txt"
csv_collection_disciplines="C:\\DEV\\CETAF\\collections_disciplines.txt"
dict_collections={}
root_url="/"
current_index_search="cetaf_passport_collections"
current_index="cetaf_passport_collections_full"
index_institution="cetaf_passport_institutions"

def find_institution(acronym_inst):
    global es
    global index_institution
    query_var={"match": {"institution_acronym": acronym_inst}}
    resp = es.search(index=index_institution, query=query_var)

    return resp["hits"]["hits"]
    
def init_collection(main_id, acronym_inst, acronym_collection):
    global dict_collections
    '''
    if main_id not in dict_collections:
        dict_collections[main_id]={}
        dict_collections[main_id][acronym_inst]={}
    if acronym_collection not in dict_collections[main_id][acronym_inst]:
        dict_collections[main_id][acronym_inst][acronym_collection]={}
        dict_collections[main_id][acronym_inst][acronym_collection]["coverage_fields"]={}
        dict_collections[main_id][acronym_inst][acronym_collection]["coverage_fields"]["countries_and_areas"]=[]
    '''
    if acronym_inst not in dict_collections:
        dict_collections[acronym_inst]={}
    if not main_id in dict_collections[acronym_inst]:
        dict_collections[acronym_inst][main_id]={}
        dict_collections[acronym_inst][main_id][acronym_collection]={}
        dict_collections[acronym_inst][main_id][acronym_collection]["coverage_fields"]={}
        dict_collections[acronym_inst][main_id][acronym_collection]["coverage_fields"]["countries_and_areas"]=[]
        dict_collections[acronym_inst][main_id][acronym_collection]["coverage_fields"]["taxonomic_discipline"]=[]
        
def load_file():
    global root_url
    global dict_collections
    global es
    global current_index
    global current_index_search
    geo=pnd.read_csv(csv_collection_geo, sep='\t', encoding='ISO-8859–1')
    disciplines=pnd.read_csv(csv_collection_disciplines, sep='\t', encoding='ISO-8859–1')
    for index, row in disciplines.iterrows():            
        print(row)
        acronym_institution=row["acronym"]
        collection_name=row["main_category"]
        discipline=row["category"]
        main_id=root_url+acronym_institution+"/"+collection_name
        print(acronym_institution)
        init_collection(main_id, acronym_institution, collection_name)
        dict_collections[acronym_institution][main_id][collection_name]["coverage_fields"]["main_category"]=collection_name
        #list_discipline=dict_collections[acronym_institution][main_id][collection_name]["coverage_fields"]["taxonomic_discipline"]
        #list_discipline.append(discipline)
        dict_collections[acronym_institution][main_id][collection_name]["coverage_fields"]["taxonomic_discipline"]=discipline
        print(dict_collections)
    print("---------------------------------")    
    for index, row in geo.iterrows():
        acronym_institution=row["acronym"]
        collection_name=row["main_category"]
        area= row["area"]
        main_id=root_url+acronym_institution+"/"+collection_name
        #print(acronym_institution)
        init_collection(main_id, acronym_institution, collection_name)
        list_areas=dict_collections[acronym_institution][main_id][collection_name]["coverage_fields"]["countries_and_areas"]
        list_areas.append({"area_name": area})
        dict_collections[acronym_institution][main_id][collection_name]["coverage_fields"]["countries_and_areas"]=list_areas
    print("°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°") 
    for key_inst, inst_array in  dict_collections.items():
        #print(key_inst)
        #print(inst_array)
        institution_json=find_institution(key_inst)
        if len(institution_json)>0:
            print(institution_json[0])
            inst_id=institution_json[0]["_id"]
            institution_name=institution_json[0]["_source"]["institution_name"]        
            for key_col, collection_array in inst_array.items():
                print(key_col)
                print(collection_array)
                for discipline, es_array in collection_array.items():
                    #print(discipline)
                    es_array["institution_name"]=institution_name
                    es_array["to_parent_institution"]=inst_id
                    print(es_array)
                    es.update(index=current_index_search,id=key_col,body={'doc': es_array,'doc_as_upsert':True})
                    es.update(index=current_index,id=key_col,body={'doc': es_array,'doc_as_upsert':True})
        #else:
        #    institution_name=key        
        '''
        print(key)
        #print(collection_array)
        print(key.strip("/").split("/"))
        key_inst=key.strip("/").split("/")[0]
        institution_json=find_institution(key_inst)
        #print(institution_json)
        if len(institution_json)>0:
            #print(institution_json[0])
            institution_name=institution_json[0]["_source"]["institution_name"]
        else:
            institution_name=key
        #print(institution_name)
        collection_array["institution_name"]=institution_name
        print(collection_array)
        #es.update(index=current_index_search,id=p_url,body={'doc': es_json,'doc_as_upsert':True})
        '''
        

if __name__ == "__main__":
    es =  Elasticsearch(
        ["http://ursidae.rbins.be:9200"],       
        #use_ssl = False,
        #port=9200,
        timeout=30
    )
    load_file()