import requests,json, sys, collections
from requests.auth import HTTPBasicAuth
import pandas as pd
from collections import OrderedDict
from bs4 import BeautifulSoup
from deepmerge import always_merger
from copy import deepcopy



src_excel="mars_model_20201811_mapping.xlsx"
dict_mapping={}
dict_inst_urls={}
dict_concepts_url={}
dict_json_content={}
found_items={}
absent_items={}
structure_es={}
data_es={}
auth_mars = HTTPBasicAuth('ftheeten', 'mamy1999')


root_list_institutions="https://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions"

def merge_dicts(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

    
def convert_path_to_array(path, value):
    acc={}
    if  path is not None:
        tmp=path.split("/")
        print("IDEX")
        print(tmp)
        if tmp is not None:
            tmp.reverse()
            i=0
            for item in tmp:
                if i==0:
                    acc[item]=value
                else:
                    acc2={}
                    acc2[item] =acc.copy()
                    acc=acc2
                i=i+1
    return acc        
    
def copy_to_es():
    global dict_inst_urls
    global dict_concepts_url
    global found_items
    global absent_items
    global structure_es
    global data_es
    '''
    print("FOUND")
    for key, items in found_items.items():
        print(key)
        print(items)
    print("NOT_FOUND")
    for key, items in absent_items.items():
        print(key)
        print(items)
    '''
    print("")
    print("ES_STRUCTURE")
    for index, nested in structure_es.items():
        print("index="+index)
        for key, items in nested.items():
            print("KEY="+str(key))
            print(items)
            for items2 in items:
                url_concept=items2['url']
                url_field=items2['field']
                for key3, item3 in dict_inst_urls.items():
                    inst_url=item3["url"]
                    main_url=inst_url+url_concept
                    if main_url in found_items:
                        #print("FOUND "+main_url)
                        
                        #print(found_items[main_url])
                        if url_field in found_items[main_url]:
                            print("FIELD_FOUND "+url_field+ " URL=" +main_url+ " KEY="+key)
                            json_rep=convert_path_to_array(key, found_items[main_url][url_field])
                            tmp={}
                            print(json_rep)
                            if inst_url not in data_es:
                                data_es[inst_url]={}
                            tmp[inst_url]={}
                            if index not in data_es[inst_url]:
                                data_es[inst_url][index]={}
                            tmp[inst_url][index]=[json_rep]
                            main=deepcopy(data_es[inst_url][index])
                            merged=always_merger.merge(main,tmp)
                            print("MERGED=>")
                            print(merged)
                            print("<=")
                            data_es[inst_url][index]=merged
    '''            
    for key, item in dict_inst_urls.items():
        #print(key)
        #print(item["url"])        
        inst_url=item["url"]
        for concept_url, list_concepts in dict_concepts_url.items():
            main_url=inst_url+concept_url
            print(main_url)
            if main_url in found_items:
               print("FOUND")
               for field, value in found_items[main_url].items():
                    print(field)
                    print(value)
    '''
    #for key, items in found_items.items():
    #    print(key)
    #    print(items) 

        
def check_concept_found():
    global dict_json_content
    global dict_concepts_url
    global found_items
    global absent_items
    for inst_url, dict_var in dict_json_content.items():
        concept_url=dict_var["mars_concept_prefix"]
        print("concept_url :"+concept_url)
        #print(concept_url)
        for concept in dict_concepts_url[concept_url]:
            #print(concept)
            if concept in dict_var:
                #print("concept "+concept+ " found for " + inst_url)
                #print("value is " + str(dict[concept]))
                type_val=type(dict_var[concept])
                #print("TYPE "+str(type_val)+" "+concept)
                if  isinstance(dict_var[concept],dict):
                    if "content-type" in dict_var[concept] and "data" in dict_var[concept]:
                        if dict_var[concept]["content-type"]=="text/html":
                            #print("IS_HTML "+concept)
                            #print(dict_var[concept])
                            dict_var[concept]["data"]
                            
                            table_data = [[cell.text.replace('\xa0', ' ').strip() for cell in row("td")]
                                                     for row in BeautifulSoup(dict_var[concept]["data"])("tr")]
                            
                            if table_data==[['']]:
                                #print("EMPTY_TABLE")
                                if inst_url not in absent_items:
                                    absent_items[inst_url]=[]
                                absent_items[inst_url].append(concept)
                            else:
                                if inst_url not in found_items:
                                    found_items[inst_url]={}
                                found_items[inst_url][concept]=table_data
                            #json_table=json.dumps(OrderedDict(table_data))
                            #print(json_table)
                    
                elif dict_var[concept] is None:
                    if inst_url not in absent_items:
                        absent_items[inst_url]=[]
                    absent_items[inst_url].append(concept)
                elif dict_var[concept] ==[]:
                    if inst_url not in absent_items:
                        absent_items[inst_url]=[]
                    absent_items[inst_url].append(concept)
                elif len(str(dict_var[concept]).strip())==0:
                    if inst_url not in absent_items:
                        absent_items[inst_url]=[]
                    absent_items[inst_url].append(concept)
                else:
                    if inst_url not in found_items:
                        found_items[inst_url]={}
                    found_items[inst_url][concept]=dict_var[concept]   
            else: #dead code ?
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
        print(data.encoding)
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
    global structure_es
    p_sheet.fillna('', inplace=True)
    for idx, row in p_sheet.iterrows():
        if 'es_index' in row and 'field' in row and 'es_field' in row and 'url' in row:
            if len(row['es_index'].strip())>0 and len(row['field'].strip())>0 and len(row['es_field'].strip())>0 and len(row['url'].strip())>0 :
                #print("URL"+row['url'])
                if row['es_index'] not in dict_mapping:
                    dict_mapping[row['es_index']]={}
                dict_mapping[row['es_index']][row['field']]=row
                if row['url'] not in dict_concepts_url:
                    dict_concepts_url[row['url']]=[]
                dict_concepts_url[row['url']].append(row["field"])
                if str(row['es_index']) not in  structure_es:
                    structure_es[str(row['es_index'])]={}
                if str(row['es_field']) not in  structure_es[str(row['es_index'])]:
                    structure_es[str(row['es_index'])][str(row['es_field'])]=[]
                structure_es[str(row['es_index'])][str(row['es_field'])].append({"url":row['url'] ,"field":row['field'] })    
            
   

def parse(p_file):
    global dict_mapping
    sheet_to_df_map = pd.read_excel(p_file, sheet_name=None, dtype = str)
    sheet_to_df_map
    #print(sheet_to_df_map)
    for file, items in sheet_to_df_map.items():
        #print("file ="+file)
        parse_sheet(items)    

if __name__ == "__main__":
    get_mars_url(root_list_institutions)
    parse(src_excel)
    test_object_exists()
    copy_to_es()
    print(data_es)
    '''
    print("MAPPING")
    print("=======")
    print(dict_mapping)
    print("URL")
    print("=======")
    print(dict_concepts_url)  
    #print("JSON")
    #print("=======")
    #print(dict_json_content)
    
    
    print("FOUND")
    print("=======")
    print(found_items)
    print("ABSENT")
    print("=======")
    print(absent_items)
    '''    