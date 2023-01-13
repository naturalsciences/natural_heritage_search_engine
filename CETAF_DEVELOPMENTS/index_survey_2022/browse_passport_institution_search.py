import argparse
import requests
from requests.auth import HTTPBasicAuth
import json
from elasticsearch import Elasticsearch


root_list_institutions="https://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions"
auth_mars = HTTPBasicAuth('', '')
es_json={}
review_date=None
current_index="cetaf_passport_institutions"

def null_str(val):
    if val=="":
        val=None
    return val
    
def get_value(p_dict, key):
    returned=""
    if key in p_dict:
        if p_dict[key] is not None:
            returned=p_dict[key]
    return returned

def parse_institution_research(base_url, es_dict, suffix_institution_detail="/4-cetaf-passport-research"):
    p_url=base_url+suffix_institution_detail
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars, verify=False)
    dict_mars=json.loads(data.text)
    if "research_field_list" in dict_mars:
        research_fields=dict_mars["research_field_list"]
        es_dict["research"]={}
        es_dict["research"]["research_fields"]=research_fields
    return es_dict 

def parse_institution_detail(base_url, es_dict, suffix_institution_detail="/1-cetaf-passport-administration"):
    p_url=base_url+suffix_institution_detail
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars, verify=False)
    dict_mars=json.loads(data.text)
    country=dict_mars["address_country"]
    if country is not None:
        if isinstance(country, list):
            if len(country)>0:
                country=country[0]
    print(country)
    es_dict["institution_address"]={}
    es_dict["institution_address"]["country"]=null_str(country)
    institution_email= get_value(dict_mars, "address_email")
    dir_surname= get_value(dict_mars, "direction_first_name_s_")
    dir_name= get_value(dict_mars, "direction_name_s")
    dir_mail= get_value(dict_mars, "direction_email")
    dir_title= get_value(dict_mars, "direction_title")
    if dir_title!="":
        dir_title=dir_title+" "
    #print(dir_name)
    #print(dir_mail)
    if dir_name !="" and dir_mail !="":
        #print(dir_name)
        #print(dir_mail)
        if dir_surname !="":
           dir_name=dir_surname+ " "+dir_name
        es_dict["director_or_legal_representative"]={}
        es_dict["director_or_legal_representative"]["dir_rep_name"]= null_str(dir_name)    
        es_dict["director_or_legal_representative"]["dir_rep_email"]= null_str(dir_mail)        
        es_dict["director_or_legal_representative"]["dir_rep_title"]= null_str(dir_title)        
    es_dict["institution_address"]["email"]=institution_email
    return es_dict

def parse_institution(p_url):
    global es_json
    global review_date
    global current_index
    es_json={}
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars, verify=False)
    dict_mars=json.loads(data.text)
    institution_id=dict_mars["institution_id"]
    main_name=dict_mars["title"]
    grid_id=dict_mars["grid_id"]
    grscicoll_code=dict_mars["grscicoll_code"]

    isni_id=dict_mars["isni_id"]
    name_1=dict_mars["original_name_1"]
    lang_name_1=dict_mars["original_name_1_language"]
    update_date=dict_mars["modified"]
    print(name_1)
    print("-------------------")
    #print(dict_mars)
    #es_json["_id"]=institution_id
    es_json["institution_name"]=main_name
    es_json=parse_institution_detail(p_url, es_json)
    es_json=parse_institution_research(p_url, es_json)
    if update_date>=review_date:
        es.update(index=current_index,id=p_url,body={'doc': es_json,'doc_as_upsert':True})
     
     
def explore_mars(p_url):
    global auth_mars 
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars, verify=False)
    dict=json.loads(data.text)
    go=True
    i=0
    while go:
        current=dict["batching"]["@id"]
        if "next" in dict["batching"]:
            next=dict["batching"]["next"]
        last=dict["batching"]["last"]
        
        for inst in dict["items"]:
            print(i)
            print(inst["@id"])
            data2=requests.get(inst["@id"], headers={'accept':'application/json'},auth=auth_mars, verify=False)
            dict2=json.loads(data2.text)
            if "institution_id" in dict2:
                print("IS_MUSEUM")
                parse_institution(inst["@id"])
                #parse_excel( inst["@id"], src_excel)
                i=i+1
        if current==last:
           go=False
        else:
            #print("GO NEXT" + next)
            data=requests.get(next, headers={'accept':'application/json'},auth=auth_mars, verify=False)
            dict=json.loads(data.text)
            
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--user_mars")
    parser.add_argument("--password_mars")
    parser.add_argument("--source_excel")
    parser.add_argument("--es_server")
    parser.add_argument("--review_date")
    args = parser.parse_args()
    
    review_date=args.review_date
    es =  Elasticsearch(
        [args.es_server],       
        #use_ssl = False,
        #port=9200,
        timeout=30
    )
    auth_mars = HTTPBasicAuth(args.user_mars, args.password_mars)
    src_excel=args.source_excel
    explore_mars(root_list_institutions)