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
    
def parse_html_table(var_html, tags=r'p|li'):
    elems=BeautifulSoup(var_html).find_all(re.compile(tags))
    elems=[var.get_text().strip() for var in elems if var.get_text().strip() !='']
    return elems

def detail_collection(p_url, es_json):
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars, verify=False)
    dict_mars=json.loads(data.text)
    exists=dict_mars["exist_in_this_institution"]
    if exists.lower()!="no":
        print("EXISTS")
    
    
def browse_collections(p_url, es_json, url_suffix="/2-cetaf-passport-collections/collections"):
    new_url=p_url+url_suffix
    data=requests.get(new_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars, verify=False)
    dict_mars=json.loads(data.text)
    items=dict_mars["items"]
    #print(items)
    for item in items:
        if item["@type"]=="nh_collection":
            id=item["@id"]
            name=item["title"]
            print(id)
            print(name)
            detail_collection(id,es_json)
    

def parse_institution(p_url):
    global es_json
    global review_date
    global current_index
    es_json={}
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars, verify=False)
    dict_mars=json.loads(data.text)
    institution_id=dict_mars["institution_id"]
    main_name=dict_mars["title"]
    browse_collections(p_url,es_json )
    #if update_date>=review_date:
    #    es.update(index=current_index,id=p_url,body={'doc': es_json,'doc_as_upsert':True})
     
     
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