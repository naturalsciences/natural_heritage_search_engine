import requests,json, sys, collections, argparse
from requests.auth import HTTPBasicAuth
from transfer_mars_lib import *
from elasticsearch import Elasticsearch
import copy
import sys

es=None
create_es=False
root_list_institutions="https://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions"
url_suffix_facilities="/3-cetaf-passport-facilities/list"
url_suffix_address="/1-cetaf-passport-administration"
es_server_name=None
data_index="cetaf_passport_facilities"
current_institution_name=""
current_country=""
current_institution_url=""
check_date=None
check_date_default="2021-01-01T00:00:00+02:00"



    
def get_facility(p_url, auth_mars, p_type, p_tech_type):
    print(p_url)
    global es
    global data_index
    global current_institution_name
    global current_country
    global current_institution_url
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    title=p_dict["title"]
    if not title is None:
        current_json={}
        current_json["laboratories"]=p_type
        current_json["facility_type"]=p_type
        current_json["facility_name"]=title
        current_json["institution_name"]=current_institution_name
        current_json["facility_address"]={}
        current_json["facility_address"]["country"]=current_country
        current_json["contact"]={}
        mail=get_value_field(p_dict, p_tech_type +"_email")
        if not mail is None:
            first_name=none_to_empty(get_value_field(p_dict, p_tech_type +"_first_name_s"))
            surname=none_to_empty(get_value_field(p_dict, p_tech_type +"_name_s"))
            title=get_value_field(p_dict, p_tech_type +"_title_s")
            phone=get_value_field(p_dict, p_tech_type +"_phone")
            name_contact=first_name+" "+surname
            name_contact=name_contact.strip()
            if not title is None:
                current_json["contact"]["contact_title"]=title
            if len(name_contact)>0:
                current_json["contact"]["contact_name"]=name_contact
            if not phone is None:
                current_json["contact"]["contact_phone"]=phone
            if not mail is None:
                current_json["contact"]["contact_email"]=mail
        link=p_url
        if "facility_link" in p_dict:
            if not get_value_field(p_dict, "facility_link") is None:
               link=get_value_field(p_dict, "facility_link")
        current_json["url_id"]=link
        description=get_value_field(p_dict, p_tech_type +"_description")
        if not description is None:
            current_json["facility_description"]=description
        current_json["to_parent_institution"]=current_institution_url
        add_data_es(es, data_index, p_url, current_json )
    
def parse_facilities(p_url, auth_mars):
    print("facility list:")
    print(p_url)
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    list_collections=p_dict["items"]
    print(list_collections)
    for item in list_collections:
        print(item)
        if item["@type"]=="cetaf_passport_facility":
            print("go")
            get_facility(item["@id"], auth_mars, "facility or laboratory", "facility")
        elif item["@type"]=="cetaf_passport_equipment":
            print("go")
            get_facility(item["@id"], auth_mars, "equipment", "instrument")
    
def parse_institution(p_url, auth_mars):
    global url_suffix_facilities
    global url_suffix_address
    global current_institution_name
    global current_country
    global current_institution_url
    print(p_url)
    current_institution_name=""
    current_country=""
    current_institution_url=""
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)

    name_museum=p_dict["title"]
    url_country=p_url+url_suffix_address
    print(url_country)
    data2=requests.get(url_country, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict2=json.loads(data2.text)
    country=get_value_field(p_dict2, "address_country")
    if not country is None:
       if len(country)>0:
            current_country=country

    print(name_museum)
    if not name_museum is None:
       if len(name_museum.lower().strip())>0:
            current_institution_name=name_museum
            current_institution_url=p_dict["@id"]
    parse_facilities(p_url+url_suffix_facilities, auth_mars)

def get_collections(p_url, auth_mars):
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    go=True
    i=0
    while go:
        current=p_dict["batching"]["@id"]
        if "next" in p_dict["batching"]:
            next=p_dict["batching"]["next"]
        last=p_dict["batching"]["last"]
        
        for inst in p_dict["items"]:
            print(i)
            #print(inst["@id"])
            data2=requests.get(inst["@id"], headers={'accept':'application/json'}, auth=auth_mars)
            dict2=json.loads(data2.text)
            if "institution_id" in dict2:
                #print("IS_MUSEUM")
                parse_institution( inst["@id"], auth_mars)
                i=i+1
        if current==last:
           go=False
        else:
            #print("GO NEXT" + next)
            data=requests.get(next, headers={'accept':'application/json'}, auth=auth_mars)
            p_dict=json.loads(data.text)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--es_server")
    parser.add_argument("--check_date", default=check_date_default)
    parser.add_argument("--user_mars")
    parser.add_argument("--password_mars")
    
    args = parser.parse_args()
    check_date=args.check_date
    print(check_date)
    print(args.es_server)
    es =  Elasticsearch(
        [args.es_server],       
        use_ssl = False,
        port=9200,
        timeout=30
    )
    #get_collections(root_list_institutions)
    auth_mars = HTTPBasicAuth(args.user_mars, args.password_mars)
    get_collections(root_list_institutions, auth_mars)
    #parse_institution("https://collections.naturalsciences.be/cpb/nh-collections/countries/germany/de-zfmk", auth_mars)