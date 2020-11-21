import requests,json, sys
from requests.auth import HTTPBasicAuth
import pandas as pd

src_excel="mars_model_20201811_mapping.xlsx"
dict_mapping={}
dict_inst_urls={}
dict_concepts_url={}
dict_json_content={}
found_items={}
absent_items={}
auth_mars = HTTPBasicAuth('', '')


root_list_institutions="http://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions"

def copy_to_es():
    global found_items
    global absent_items
    print("FOUND")
    for key, items in found_items.items():
        print(key)
        print(items)
    print("NOT_FOUND")
    for key, items in absent_items.items():
        print(key)
        print(items)
    
        
def check_concept_found():
    global dict_json_content
    global dict_concepts_url
    global found_items
    global absent_items
    for inst_url, dict in dict_json_content.items():
        concept_url=dict["mars_concept_prefix"]
        print("concept_url :"+concept_url)
        #print(concept_url)
        for concept in dict_concepts_url[concept_url]:
            #print(concept)
            if concept in dict:
                #print("concept "+concept+ " found for " + inst_url)
                #print("value is " + str(dict[concept]))
                if inst_url not in found_items:
                    found_items[inst_url]={}
                found_items[inst_url][concept]=dict[concept]   
            else:
                #print("concept "+concept+ " NOT FOUND for " + inst_url)
                if inst_url not in absent_items:
                    absent_items[inst_url]=[]
                absent_items[inst_url].append(concept)
               
def load_content(p_url):
    global dict_concepts_url
    global dict_json_content
    for concept_url, list_concepts in dict_concepts_url.items():
        main_url=p_url+concept_url
        #print(main_url)
        data=requests.get(main_url, headers={'accept':'application/json'}, auth=auth_mars)
        dict=json.loads(data.text)
        print(concept_url)
        dict["mars_concept_prefix"]=concept_url
        dict_json_content[main_url]=dict

def test_object_exists():
    global dict_inst_urls    
    for key, item in dict_inst_urls.items():
        #print(key)
        #print(item["url"])        
        load_content(item["url"])
    check_concept_found()
       
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
            #print(inst["@id"])
            data2=requests.get(inst["@id"], headers={'accept':'application/json'},auth=auth_mars)
            dict2=json.loads(data2.text)
            #print(dict2["institution_id"])
            json_tmp={"url":inst["@id"], "institution_id": dict2["institution_id"], "institution_name": dict2["title"]}
            dict_inst_urls[dict2["institution_id"].lower()]=json_tmp
        if current==last:
           go=False
        else:
            #print("GO NEXT" + next)
            data=requests.get(next, headers={'accept':'application/json'},auth=auth_mars)
            dict=json.loads(data.text)

def parse_sheet(p_sheet):
    global dict_mapping
    for idx, row in p_sheet.iterrows():
        if 'es_index' in row and 'field' in row and 'es_field' in row and 'url' in row:
            #print("URL"+row['url'])
            if row['es_index'] not in dict_mapping:
                dict_mapping[row['es_index']]={}
            dict_mapping[row['es_index']][row['field']]=row
            if row['url'] not in dict_concepts_url:
                dict_concepts_url[row['url']]=[]
            dict_concepts_url[row['url']].append(row["field"])
            
   

def parse(p_file):
    global dict_mapping
    sheet_to_df_map = pd.read_excel(p_file, sheet_name=None)
    #print(sheet_to_df_map)
    for file, items in sheet_to_df_map.items():
        #print("file ="+file)
        parse_sheet(items)
    #print(dict_mapping)    

if __name__ == "__main__":
    get_mars_url(root_list_institutions)
    parse(src_excel)
    test_object_exists()
    copy_to_es()