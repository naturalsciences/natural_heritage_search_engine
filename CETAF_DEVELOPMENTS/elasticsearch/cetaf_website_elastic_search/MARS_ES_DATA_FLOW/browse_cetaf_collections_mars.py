import requests,json, sys
from requests.auth import HTTPBasicAuth
import dateutil
from elasticsearch import Elasticsearch

es = None
url_root = "http://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions#c0=all&b_start=0"
url_suffix_collection_list = "/2-cetaf-passport-collections"
INDEX_NAME_COLLECTIONS = "cetaf_passport_collections"
INDEX_NAME_COLLECTIONS_FULL = "cetaf_passport_collections_full"
dict_inst_urls = {}
dict_collections_url = {}
dict_collections = {}
auth_mars = HTTPBasicAuth('', '')
list_checked = []

modified_limit_iso=dateutil.parser.parse("2020-09-19T22:45:00+02:00")
main_category="Life Science"

def insert_es(json):
    global main_category
    global INDEX_NAME_COLLECTIONS, INDEX_NAME_COLLECTIONS_FULL
    to_write={}
    to_write["url_id"]=json["url"]
    
    to_write["coverage_fields"]={}
    to_write["coverage_fields"]["main_category"]=main_category    
    to_write["coverage_fields"]["name_taxonomic_category"]=json["title"]
    
    to_write["to_parent_institution"]=json["institution_id"]
    to_write["institution_name"]=json["institution_name"]
    to_write["collection_name"]=json["title"]
    
    to_write["size_and_digitisation_fields"]={}
    to_write["size_and_digitisation_fields"]["specimens_count"]=json["number_of_specimens"]
    to_write["size_and_digitisation_fields"]["primary_types_count"]=json["primary_types"]
    to_write["size_and_digitisation_fields"]["other_size_indicators"]=json["other_size_indicator"]
    
    to_write["size_and_digitisation_fields_sum_all"]={}
    to_write["size_and_digitisation_fields_sum_all"]["specimens_count"]=json["number_of_specimens"]
    to_write["size_and_digitisation_fields_sum_all"]["primary_types_count"]=json["primary_types"]
    to_write["size_and_digitisation_fields_sum_all"]["other_size_indicators"]=json["other_size_indicator"]
    es.index(index=INDEX_NAME_COLLECTIONS, doc_type= "_doc",id=to_write["url_id"], body=to_write)
    
    to_write["collection_description"]=json["description"]
    es.index(index=INDEX_NAME_COLLECTIONS_FULL, doc_type= "_doc",id=to_write["url_id"], body=to_write)

def check_exists(param):
    try:
        if not param is None:
            return param
        else:
             return None        
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return None

def array_key_exists(array, elem, nested=None):
    try:
        if elem in array:
            if nested:
                if nested in array[elem]:
                    return check_exists(array[elem][nested])
                else:
                    return None
            else:
                return check_exists(array[elem])
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return None
            
def browse_collection(p_url, institution_id, institution_name):
    try:
        global dict_collections
        global list_checked
        data=requests.get(p_url, headers={'accept':'application/json'},auth=auth_mars)
        dict=json.loads(data.text)
        if "items" in dict:
            for elem in dict["items"]:
                if elem["@type"]=="nh_collection":
                    data2=requests.get(elem["@id"], headers={'accept':'application/json'},auth=auth_mars)
                    dict2=json.loads(data2.text)                
                    modification_date=dict2["modified"]
                    modification_date_iso = dateutil.parser.parse(modification_date)
                    #modified_limit_iso = dateutil.parser.parse(modified_limit)
                    #print("ID:"+dict2["@id"])
                    #print(modification_date_iso)
                    #print(modified_limit_iso)
                    if modification_date_iso>=modified_limit_iso:
                        print("GO !!!!!!!!!!!!!!!!!!!!!!" + dict2["@id"])
                        dict_collections[dict2["@id"]]={ 
                                                           "url": array_key_exists(dict2,"@id"),
                                                           "institution_id":institution_id,
                                                           "institution_name":institution_name,
                                                           "title": array_key_exists(dict2,"title"),
                                                           "modification_date": array_key_exists(dict2,"modified"),
                                                           "creation_date": array_key_exists(dict2,"created"),
                                                           "description": array_key_exists(dict2,"description"),
                                                           "number_of_specimens": array_key_exists(dict2,"number_of_specimens_"),
                                                           "primary_types": array_key_exists(dict2,"primary_types"),
                                                           "other_size_indicator": array_key_exists(dict2,"other_size_indicator", "data"),
                                                       }
                        print(dict_collections[dict2["@id"]])
                        insert_es(dict_collections[dict2["@id"]])
                    #print("CALL FROM "+dict2["@id"])
                    if dict2["@id"] not in list_checked:
                        list_checked.append(dict2["@id"])
                        browse_collection(dict2["@id"], institution_id, institution_name)
    except:
        print("Unexpected error:", sys.exc_info())
        return None                        
            
def browse_folder(dict, institution_id, institution_name):
    #print(dict["items"])    
    for elem in dict["items"]:
        #print(elem["@id"])
        if elem["@type"]=="Folder":
                print("Folder="+elem["@id"])
                browse_collection(elem["@id"], institution_id, institution_name)
                    

def get_gollection_url(key):
    global url_suffix_collection_list    
    url=dict_inst_urls[key]["url"]+url_suffix_collection_list
    print("try to browse "+url)
    institution_id = dict_inst_urls[key]["institution_id"]
    institution_name = dict_inst_urls[key]["institution_name"]
    data=requests.get(url, headers={'accept':'application/json'},auth=auth_mars)
    dict=json.loads(data.text)
    
    if "batching" in dict:
        go=True
        while go:
            current=dict["batching"]["@id"]
            if "next" in dict["batching"]:
                next=dict["batching"]["next"]
            last=dict["batching"]["last"]
            browse_folder(dict, institution_id, institution_name)
            if current==last:
               go=False
            else:
                print("GO NEXT" + next)
                data=requests.get(next, headers={'accept':'application/json'},auth=auth_mars)
                dict=json.loads(data.text)
    else:
        print("no batching")
        browse_folder(dict, institution_id, institution_name)

def get_mars_url(p_url):
    
    global dict_inst_urls
    data=requests.get(p_url, headers={'accept':'application/json'}, auth=auth_mars)
    dict=json.loads(data.text)
    go=True
    while go:
        current=dict["batching"]["@id"]
        if "next" in dict["batching"]:
            next=dict["batching"]["next"]
        last=dict["batching"]["last"]
        for inst in dict["items"]:
            print(inst["@id"])
            data2=requests.get(inst["@id"], headers={'accept':'application/json'},auth=auth_mars)
            dict2=json.loads(data2.text)
            print(dict2["institution_id"])
            json_tmp={"url":inst["@id"], "institution_id": dict2["institution_id"], "institution_name": dict2["title"]}
            dict_inst_urls[dict2["institution_id"].lower()]=json_tmp
        if current==last:
           go=False
        else:
            print("GO NEXT" + next)
            data=requests.get(next, headers={'accept':'application/json'},auth=auth_mars)
            dict=json.loads(data.text)
    #print(dict_inst_urls)
    

if __name__ == "__main__":
    es =  Elasticsearch(
        ['ursidae.rbins.be'],       
        use_ssl = False,
        port=9200,
    )
    get_mars_url(url_root)
    for key, item in dict_inst_urls.items():
        print(key)
        print(item)
        get_gollection_url(key)
    for key, item in dict_collections.items():
        print(key)
        print(item)
    #print(dict_inst_urls)
