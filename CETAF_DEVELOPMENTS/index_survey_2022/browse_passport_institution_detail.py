import argparse
import requests
from requests.auth import HTTPBasicAuth
import json
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import re
from collections import OrderedDict

root_list_institutions="https://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions"
auth_mars = HTTPBasicAuth('', '')
es_json={}
review_date=None
current_index="cetaf_passport_institutions_full"

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
    
def parse_html_table(var_html, tags=r'p|li'):
    elems=BeautifulSoup(var_html).find_all(re.compile(tags))
    elems=[var.get_text().strip() for var in elems if var.get_text().strip() !='']
    return elems    

def parse_taxonomic_expertise(base_url, es_dict, suffix_institution_detail="/8-cetaf-passport-interests-involvement/5-cetaf-passport-taxonomic-expertise"):
    p_url=base_url+suffix_institution_detail
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars, verify=False)
    dict_mars=json.loads(data.text)
    html_interest=dict_mars["main_areas_of_taxonomic_expertise"]
    if html_interest is not None:
        if 'content-type' in html_interest and 'data' in html_interest:
            if html_interest['content-type'] == 'text/html' :
                interests=html_interest["data"]
                print("expertise=>")
                print(interests)
                
                elems=parse_html_table(interests)
                #print(elems)
                
                #pb if div
                elems2=[]
                divs=BeautifulSoup(interests).find_all(re.compile("div"))
                for div in divs:
                    #print("test")
                    #print(str(div))
                    #print(type(str(div)))
                    test_nested=BeautifulSoup(str(div)).find_all(re.compile("p|li"))
                    #print("REPLY=")
                    if len(test_nested)==0:
                        elems2.append(BeautifulSoup(str(div)).get_text().strip())
                if len(elems2)>0:
                    if elems is None:
                        elems=elems2
                    else:
                        elems= elems+elems2
                if elems is not None:
                    if len(elems)>0:
                        print(list(OrderedDict.fromkeys(elems))  )
                        es_dict["main_areas_of_taxonomic_expertise"]=list(OrderedDict.fromkeys(elems))                
    return es_dict 
    
def parse_topics_of_interest(base_url, es_dict, suffix_institution_detail="/5-cetaf-passport-taxonomic-expertise/8-cetaf-passport-interests-involvement" ):
    p_url=base_url+suffix_institution_detail
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars, verify=False)
    dict_mars=json.loads(data.text)
    html_interest=dict_mars["main_topics_of_current_interest_for_your_institution"]
    if html_interest is not None:
        if 'content-type' in html_interest and 'data' in html_interest:
            if html_interest['content-type'] == 'text/html' :
                interests=html_interest["data"]
                print("interest=>")
                print(interests)
                elems=parse_html_table(interests)               
                if elems is not None:
                    if len(elems)>0:
                        print(list(OrderedDict.fromkeys(elems))  )
                        es_dict["current_topics_of_interest"]=list(OrderedDict.fromkeys(elems))    
    return es_dict
    
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
    address_street=dict_mars["address_street"]
    address_city=dict_mars["address_city"]
    address_postcode=dict_mars["address_postcode"]
    es_dict["institution_address"]={}
    es_dict["institution_address"]["country"]=null_str(country)
    es_dict["institution_address"]["street"]=null_str(address_street)
    es_dict["institution_address"]["city"]=null_str(address_city)
    es_dict["institution_address"]["postcode"]=null_str(address_postcode)
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
    chart_url=dict_mars["structure_chart_url"]        
    es_dict["institution_address"]["email"]=institution_email
    return es_dict

def parse_institution(p_url):
    global es_json
    global review_date
    global current_index
    es_json={}
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars, verify=False)
    dict_mars=json.loads(data.text)
    institution_id=get_value(dict_mars,"institution_id")
    main_name=get_value(dict_mars,"title")
    print(main_name)
    print("----------------------------------------------------------")
    grid_id=get_value(dict_mars,"grid_id")
    grscicoll_code=get_value(dict_mars,"grscicoll_code")

    isni_id=get_value(dict_mars,"isni_id")
    description=get_value(dict_mars,"description")
    type_of_institution=get_value(dict_mars,"type_of_institution")
    if isinstance(type_of_institution, list):
         if len(type_of_institution)>0:
            type_of_institution=", ".join(type_of_institution)
    name_1=get_value(dict_mars,"original_name_1")
    lang_name_1=get_value(dict_mars,"original_name_1_language")
    name_2=get_value(dict_mars,"original_name_2")
    lang_name_2=get_value(dict_mars,"original_name_2_language")
    name_3=get_value(dict_mars,"original_name_3")
    lang_name_3=get_value(dict_mars,"original_name_3_language")
    
    
    
    list_inst=[]
    
    if name_1 !="" and lang_name_1!="":
        list_inst.append({"lang": lang_name_1, "translated_name": name_1})
    if name_2 !="" and lang_name_2!="":
        list_inst.append({"lang": lang_name_2, "translated_name": name_2})
    if list_inst !="" and lang_name_3!="":
        list_inst.append({"lang": lang_name_3, "translated_name": name_3})
        
    update_date=get_value(dict_mars,"modified")
    
    #print(dict_mars)
    #es_json["_id"]=institution_id
    es_json["institution_name"]=main_name
    es_json["institution_description"]=null_str(description)
    es_json=parse_institution_detail(p_url, es_json)
    es_json=parse_institution_research(p_url, es_json)
    es_json=parse_topics_of_interest(p_url, es_json)
    es_json=parse_taxonomic_expertise(p_url, es_json)
    es_json["organisation"]={}
    es_json["organisation"]["type_of_institution"]=null_str(type_of_institution)
    es_json["identification_fields"]={}
    es_json["identification_fields"]["original_name"]=list_inst
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