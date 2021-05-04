import requests,json, sys, collections, argparse
from requests.auth import HTTPBasicAuth
from transfer_mars_lib import *
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import copy
import sys

es=None
create_es=False
root_list_institutions="https://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions"
url_suffix_address="/1-cetaf-passport-administration"
type_expertise="cetaf_passport_taxonomic_expertise"
type_staff="staff_member"
es_server_name=None
data_index="cetaf_passport_expertises"
current_institution_name=""
current_institution_acronym=""
current_country=""
current_institution_url=""
check_date=None
check_date_default="2021-01-01T00:00:00+02:00"
current_json={}


def handle_people(p_url, auth_mars):
    global current_json
    global data_index
    global es
    global current_institution_url
    global current_institution_name
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    current_json={}
    name=[]
    first_name= get_value_field(p_dict, "first_name")
    if first_name is not None:
        name.append(first_name)
    last_name= get_value_field(p_dict, "last_name")
    if last_name is not None:
        name.append(last_name)
    name_string=" ".join(name)
    if len(name)>0:
        print("mail")
        mail=get_value_field(p_dict, "email")        
        current_json["person"]={}
        current_json["person"]["name"]=name_string
        description=get_value_field(p_dict, "description")
        current_json["person"]["person_description"]=description
        dedication=get_value_field(p_dict, "full_time_equivalent")
        current_json["dedication"]=dedication
        current_json["to_parent_collection_in_institution"]=[]
        current_json["country_en"]=current_country
        new_inst={}
        new_inst["institution_name"]=current_institution_name        
        parent_coll=None
        if "parent" in p_dict:
            if "title" in p_dict["parent"]:
                parent_coll=get_value_field(p_dict["parent"], "title")
        
        new_inst["collection_name"]=parent_coll
        new_inst["institution_acronym"]=current_institution_acronym
        current_json["to_parent_collection_in_institution"].append(new_inst)
        if "expertise_division" in p_dict:
            current_json["areas_of_expertise"]=p_dict["expertise_division"]
        if "expertise_description" in p_dict:
            if not p_dict["expertise_description"] is None:
                if "data" in p_dict["expertise_description"]:
                    if not p_dict["expertise_description"]["data"] is None:
                        html_tmp=p_dict["expertise_description"]["data"]
                        html_tmp_parser= BeautifulSoup(html_tmp, 'html.parser')
                        list_exp_html = html_tmp_parser.findAll('p')
                        print(list_exp_html)
                        list_exp=[x.get_text() for x in list_exp_html]
                        print(list_exp)
                        current_json["taxonomic_fields"]=list_exp
        title=get_value_field(p_dict, "staff_title_s")
        current_json["seniority"]=title
        orcid_id=get_value_field(p_dict, "orcid_id")
        if orcid_id is not None:
            current_json["person_identifier"]={}
            current_json["person_identifier"]["identifier_protocol"]="orcid"
            current_json["person_identifier"]["identifier_value"]=orcid_id
        
        add_data_es(es, data_index, p_url, current_json )
        
def parse_people(p_url, auth_mars):
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    if "items" in p_dict:
        for item in p_dict['items']:
            #print(item)
            if "@type" in item and "@id" in item:
                if item["@type"]==type_staff:
                    print("STAFF_FOUND")
                    handle_people(item["@id"], auth_mars)
                   
    
def parse_institution(p_url, auth_mars):
    global current_institution_url
    global current_institution_name   
    global url_suffix_address
    global current_country
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    current_institution_url=p_url
    #print(p_dict)

    if "title" in p_dict:
        name_museum=p_dict["title"]
        url_country=p_url+url_suffix_address
        #print(url_country)
        data2=requests.get(url_country, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
        p_dict2=json.loads(data2.text)
        country=get_value_field(p_dict2, "address_country")
        if not country is None:
            if len(country)>0:
                current_country=country
        if not name_museum is None:
            if len(name_museum.lower().strip())>0:
                current_institution_name=name_museum
                if "items" in p_dict:
                    for item in p_dict['items']:
                        #print(item)
                        if "@type" in item and "@id" in item:
                            if item["@type"]==type_expertise:
                                #print("FOUND")
                                #print(item["@id"])
                                parse_people(item["@id"],auth_mars) 
            
def get_collections(p_url, auth_mars):
    global current_institution_acronym
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
            #print(i)
            #print(inst["@id"])
            data2=requests.get(inst["@id"], headers={'accept':'application/json'}, auth=auth_mars)
            dict2=json.loads(data2.text)
            if "institution_id" in dict2:
                #print("IS_MUSEUM")
                current_institution_acronym=dict2["institution_id"]
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