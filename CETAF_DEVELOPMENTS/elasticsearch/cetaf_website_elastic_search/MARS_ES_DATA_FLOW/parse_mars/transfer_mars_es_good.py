import argparse
import requests,json, sys, collections
from requests.auth import HTTPBasicAuth
import pandas as pd
from collections import OrderedDict, ChainMap
from bs4 import BeautifulSoup
from deepmerge import always_merger
from mergedeep import merge, Strategy
from copy import deepcopy
from elasticsearch import Elasticsearch


src_excel=""
data_es={}
auth_mars = HTTPBasicAuth('', '')
es=None

root_list_institutions="https://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions"
current_json={}
current_id=""


def remove_html(dict_var):
    returned=dict_var
    if  isinstance(dict_var,dict):
        if "content-type" in dict_var and "data" in dict_var:
            if dict_var["content-type"]=="text/html":
                print("IS_HTML")
                table_data = [[cell.text.replace('\xa0', ' ').strip() for cell in row("td")]
                                                     for row in BeautifulSoup(dict_var["data"])("tr")]
                if table_data==[['']]:
                    returned=[]
                else:
                    returned=table_data
    return returned

def flatten(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])
    
def convert_path_to_list(index, path, value, concatenate=None, concatenate_index=None, cluster=None, cluster_index=None):
    if isinstance(value, list):
        value=flatten(value)
        value='; '.join(value)
    elif isinstance(value, dict):
       if "download" in value:
            value=value["download"]
    if len(value.strip())>0:
        global current_json

        print("test path ="+path)
        print("test value ="+str(value))
        tmp=path.split("/")
        current_level=current_json[index]
        if tmp is not None:
            i=0
            for item in tmp:
                print("test elem ="+item)
                if i<len(tmp)-1:
                    print("GO_NEXT")
                    if item not in current_level:
                        current_level[item]={} #dict if intermediate level
                    #current_level= current_level[tmp]   
                elif i==len(tmp)-1:
                    print("GO")
                    if item not in current_level:
                        if not cluster is  None and not cluster_index is None:
                            current_level[item]=[] #assume string if last level
                            current_level[item].append(value)
                        else:
                            current_level[item]=value                    
                    else:
                        if not concatenate is None and not concatenate_index is None:
                            if not cluster is  None and not cluster_index is None:
                                if isinstance(current_level[item], list):
                                    if concatenate_index.isdigit():
                                        print("concatenate_index = "+ concatenate_index)
                                        print("len current level = "+ str(len(current_level[item])))
                                        concatenate_index=int(concatenate_index)                                    
                                        if len(current_level[item])<concatenate_index:
                                            print("STUFF")
                                            print(len(current_level[item]))
                                            print(concatenate_index-1)
                                            for j in range(len(current_level[item]), concatenate_index):
                                                print("loop")
                                                print(j)
                                                current_level[item].append("")
                                            current_level[item][concatenate_index-1]=value
                                        else:
                                            print(current_level[item][concatenate_index-1])                                    
                                            current_level[item][concatenate_index-1]=current_level[item][concatenate_index-1]+"; "+value
                                #else: NO OBJECT AS CONCATENATION HAS TO BE A CLUSTER
                        else:
                            if not cluster is  None and not cluster_index is None:
                                if isinstance(current_level[item], list):
                                    if cluster_index.isdigit():
                                        cluster_index=int(cluster_index)
                                        if len(current_level[item])<cluster_index:
                                            for j in range(len(current_level[item]), cluster_index):
                                                current_level[item].append("")
                                        current_level[item][cluster_index-1]=value
                            else:
                                current_level[item]=value
                current_level= current_level[item]   
                i=i+1

                
def get_data(p_sheet, p_url):
    global current_json
    global current_id
    global es
    current_json={}
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    dict_mars=json.loads(data.text)
    print(dict_mars)
    for idx, row in p_sheet.iterrows():
        #print(row)
        if 'es_index' in row and 'field' in row and 'es_field' in row and 'url' in row:
            if len(row['es_index'].strip())>0 and len(row['field'].strip())>0 and len(row['es_field'].strip())>0 and len(row['url'].strip())>0 :
                if not row['es_index'] in current_json:
                    current_json[row['es_index']]={}
                if not row['field'] is None:
                    source=dict_mars[row['field']]
                    if not source is None:
                        print("FIELD="+row['field'])
                        print(source)
                        source=remove_html(source)
                        
                        if 'es_use_field_name_in_data' in row:
                           if len(row['es_use_field_name_in_data'].strip())>0:
                                source= row['es_use_field_name_in_data']+": "+str(source)
                        print(source)
                        concat_flag=None
                        if "es_concatenate" in row:
                            concat_flag=row["es_concatenate"]
                        concat_index_flag=None
                        if "es_concatenate_index" in row:
                            concat_index_flag=row["es_concatenate_index"]
                        cluster_flag=None
                        if "es_cluster" in row:
                            cluster_flag=row["es_cluster"]
                        cluster_index_flag=None
                        if "es_cluster_index" in row:
                            cluster_index_flag=row["es_cluster_index"]                              
                        convert_path_to_list(row['es_index'], row["es_field"], source, concat_flag,  concat_index_flag,  cluster_flag, cluster_index_flag)
    print(current_json)
    for current_index, json_data in current_json.items():
        es_content=json_data
        es_content.pop('_id', None)
        es.update(index=current_index,id=current_id,body={'doc': es_content,'doc_as_upsert':True})    
                        
def parse_excel(p_url_institution, p_excel_file):
    global current_id
    print("parse "+p_url_institution)
    sheet_to_df_map = pd.read_excel(p_excel_file, sheet_name=None, dtype = str)
    for file, sheet in sheet_to_df_map.items():
        #print(sheet)
        sheet.fillna('', inplace=True)
        go_scan=False
        if 'es_index' in sheet.columns and 'field' in sheet.columns and 'es_field' in sheet.columns and 'url' in sheet.columns:
            #print(sheet)
            #print(len(sheet))
            if(len(sheet))>1:
                first_row=sheet.iloc[0]
                #print(first_row)
                #print(first_row['url'])
                if len(first_row['url'].strip())>0  :
                    url_page=p_url_institution+first_row['url']                    
                    current_id=p_url_institution
                    get_data(sheet, url_page)
                else:
                    print("NOGO!!!!!!!!!!!!!!!!!!!!!!!!")                
          

def get_mars_url(p_url): 
    global src_excel
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
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
            data2=requests.get(inst["@id"], headers={'accept':'application/json'},auth=auth_mars)
            dict2=json.loads(data2.text)
            if "institution_id" in dict2:
                print("IS_MUSEUM")
                parse_excel( inst["@id"], src_excel)
                i=i+1
        if current==last:
           go=False
        else:
            #print("GO NEXT" + next)
            data=requests.get(next, headers={'accept':'application/json'},auth=auth_mars)
            dict=json.loads(data.text)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--user_mars")
    parser.add_argument("--password_mars")
    parser.add_argument("--source_excel")
    parser.add_argument("--es_server")
    args = parser.parse_args()
    
    es =  Elasticsearch(
        [args.es_server],       
        use_ssl = False,
        port=9200,
    )
    auth_mars = HTTPBasicAuth(args.user_mars, args.password_mars)
    src_excel=args.source_excel
    get_mars_url(root_list_institutions)