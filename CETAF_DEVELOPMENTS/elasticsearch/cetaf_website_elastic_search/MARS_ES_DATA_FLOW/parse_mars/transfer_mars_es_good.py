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
#import pdb


src_excel=""
data_es={}
auth_mars = HTTPBasicAuth('', '')
es=None

root_list_institutions="https://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions"
current_json={}
current_id=""
explored=[]
non_clustered_concat={}
default_concatenation_character=";"


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

def get_value(row, dict_mars):
    returned = None
    source=dict_mars[row['field']]
    if not source is None:
        source=remove_html(source)
        if 'es_use_field_name_in_data' in row:
            if len(row['es_use_field_name_in_data'].strip())>0:
                source= row['es_use_field_name_in_data']+": "+str(source)
        if isinstance(source, list):
            source=flatten(source)
            source='; '.join(source)
        elif isinstance(source, dict):
            if "download" in source:
                source=source["download"]
        if len(source.strip())>0:
            if isinstance(source, list):
                source=flatten(source)
            returned=source
    return returned    
 
def create_cluster(current_index, cluster, cluster_index, fill_array):
    global current_json
    print("CLUSTER_INDEX="+cluster_index)
    zero_cluster_index=int(cluster_index)-1
    for es_field, value in fill_array.items():
        tmp=es_field.strip("/").split("/")
        parent_path=""
        selected_parent=None
        current_level=current_json[current_index]
        if tmp is not None:
            i=0
            for item in tmp:
                print("test elem ="+item)
                print("CURRENT_ELEM ="+str(current_level))
                if item not in current_level:
                    current_level[item]={}
                if i<len(tmp)-1:
                    print("GO_NEXT")
                    
                    parent_path=parent_path+"/"+item
                    if parent_path.strip().strip("/")==cluster.strip().strip("/"):
                        if not isinstance(current_level[item],list):
                            interm=current_level[item]
                            current_level[item]=[]
                            current_level[item].append(interm)
                        if len(current_level[item])<(zero_cluster_index+1):
                            for j in range(len(current_level[item]), zero_cluster_index+1):
                                current_level[item].append({})
                        current_level=current_level[item][zero_cluster_index]
                elif i==len(tmp)-1:
                    print("CURRENT_LEVEL="+str(current_level))                    
                    current_level[item]=value
                    print("INSERTED="+str(value))
                    #current_level= current_level[item]
                #print("VALUE_3="+str(value))
                #pdb.set_trace()
                
                i=i+1
            
def convert_path_to_list_cluster(current_index, p_sheet, index_rox, dict_mars, field, index, path,  cluster=None, cluster_index=None, concat_char=";"):
    global explored
    global current_json
    print("CLUSTER="+cluster)
    print("CLUSTER_INDEX="+str(cluster_index))
    print("ROW_INDEX="+str(index_rox))
    concat_list={}
    field_list={}
    
    for i in range(0, len(p_sheet.index)):
        row=p_sheet.iloc[i]
        if row["es_cluster"]==cluster and str(row["es_cluster_index"])==str(cluster_index):
            mars_concept=row['field']
            es_field=row['es_field']
            explored.append(i)
            print("CLUSTER FOUND FOR "+str(mars_concept)+" "+ str(es_field))
            value=get_value(row, dict_mars)
            if not value is None:
                print("VALUE_CLUSTER="+str(value))
                #pdb.set_trace()
                concat_flag=None
                if "es_concatenate" in row:
                    concat_flag=row["es_concatenate"]
                if concat_flag is None:
                    field_list[es_field]=value
                else:
                    if not es_field in concat_list:
                        concat_list[es_field]=value
                        print("VALUE_1="+str(value))
                        #pdb.set_trace()
                    else:
                        if "es_concatenation_character" in row:
                            if not row["es_concatenation_character"] is  None:
                                if len(row["es_concatenation_character"])>0:
                                    concat_char= row["es_concatenation_character"]
                        concat_list[es_field]=concat_list[es_field] + concat_char + value
                        print("VALUE_2="+str(value))
                        #pdb.set_trace()
    print("CLUSTER_CONCAT="+str(concat_list))
    print("CLUSTER_NON_CONCAT="+str(field_list))
    create_cluster(current_index, cluster, cluster_index, concat_list)
    create_cluster(current_index, cluster, cluster_index, field_list)
    
    
def convert_path_to_list(p_sheet, index_row, dict_mars, field, index, path, concat_flag=None, concat_char=";"):
    global explored
    global current_json
    global non_clustered_concat
    concat_list={}
    print("NOT_A_CLUSTER FIELD="+str(field))
    row=p_sheet.iloc[index_row]
    mars_concept=row['field']
    es_field=row['es_field']
    value=get_value(row, dict_mars)
    explored.append(index_row)
    if not value is None:
        print("VALUE_ROW="+str(value))
        if not concat_flag is None:
            print("CONCAT")
            print(str(non_clustered_concat))
            #insert later
            if not es_field in non_clustered_concat:
                non_clustered_concat[es_field]=value
                print("NOT_EXISTING "+str(es_field))
                #pdb.set_trace()
            else:
                non_clustered_concat[es_field]=non_clustered_concat[es_field] + concat_char + value
                print("EXISTING "+str(es_field))
                #pdb.set_trace()
            print("CONCAT"+str(value))
            
        else:
            #insert
            print("INSERT_VALUE="+str(value))
            tmp=path.split("/")
            current_level=current_json[index]
            if tmp is not None:
                i=0
                for item in tmp:
                    print("test elem ="+item)
                    print("CURRENT_LEVEL="+str(current_level))
                    if i<len(tmp)-1:
                        print("GO_NEXT")
                        if item not in current_level:
                            current_level[item]={}
                    elif i==len(tmp)-1:
                        if item not in current_level:
                            current_level[item]={}
                        current_level[item]=value
                        print("INSERTED="+str(value))
                    print("VALUE_3="+str(value))
                    #pdb.set_trace()
                    current_level= current_level[item]
                    i=i+1
                            
def get_data(p_sheet, p_url):
    global current_json
    global explored
    global current_id
    global es
    global non_clustered_concat
    global default_concatenation_character
    current_json={}
    explored=[]
    non_clustered_concat={}
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    dict_mars=json.loads(data.text)
    current_index=""
    #print(dict_mars)
    #for idx, row in p_sheet.iterrows():
    for i in range(0, len(p_sheet.index)):
        if not i in explored:
            row=p_sheet.iloc[i]
            #print(row)
            if 'es_index' in row and 'field' in row and 'es_field' in row and 'url' in row:
                if len(row['es_index'].strip())>0 and len(row['field'].strip())>0 and len(row['es_field'].strip())>0 and len(row['url'].strip())>0 :
                    if not row['es_index'] in current_json:
                        current_json[row['es_index']]={}
                        current_index=row['es_index']
                    if not row['field'] is None:
                        print("FIELD="+row['field'])
                        concat_flag=None
                        if "es_concatenate" in row:
                            concat_flag=row["es_concatenate"]
                            print("concat_flag="+str(concat_flag))
                            #pdb.set_trace()
                        concat_index_flag=None
                        if "es_cluster_index" in row:
                            concat_index_flag=row["es_cluster_index"]
                        concat_sign=default_concatenation_character
                        if "es_concatenation_character" in row:
                            if not row["es_concatenation_character"] is  None:
                                if len(row["es_concatenation_character"])>0:
                                    concat_sign= row["es_concatenation_character"]
                        cluster_flag=None
                        if "es_cluster" in row:
                            cluster_flag=row["es_cluster"]
                        cluster_index_flag=None
                        if "es_cluster_index" in row:
                            cluster_index_flag=row["es_cluster_index"]
                        if not cluster_flag is None:
                            if len(str(cluster_flag).strip())==0:
                                cluster_flag=None
                        if not concat_flag is None:
                            if len(str(concat_flag).strip())==0:
                                print("REINIT")
                                #pdb.set_trace()
                                concat_flag=None
                        if not cluster_index_flag is None:
                            if len(str(cluster_index_flag).strip())==0:
                                cluster_index_flag=None
                        
                        if not cluster_flag is None and not cluster_index_flag is None:
                            print("CLUSTER")
                            #pdb.set_trace()                            
                            convert_path_to_list_cluster(current_index, p_sheet, row.name, dict_mars, row['field'], row['es_index'], row["es_field"],   cluster_flag,  cluster_index_flag)
                        else:
                            if not concat_flag is None:
                                print("WAIT")
                                #pdb.set_trace()
                            convert_path_to_list(p_sheet, i, dict_mars, row['field'], row['es_index'], row["es_field"],  concat_flag, concat_sign)
    
    for path_concat, json_value in non_clustered_concat.items():
        tmp=path_concat.split("/")
        current_level=current_json[current_index]
        if tmp is not None:
            i=0
            for item in tmp:
                print("test elem ="+item)
                if i<len(tmp)-1:
                    print("GO_NEXT")
                    if item not in current_level:
                        current_level[item]={}
                elif i==len(tmp)-1:
                    if item not in current_level:
                        current_level[item]={}
                    current_level[item]=json_value
                    print("INSERTED_CONCAT="+str(json_value))
                print("VALUE_CONCAT="+str(json_value))
                #pdb.set_trace()
                current_level= current_level[item]
                i=i+1
    print(current_json)
    print("DEBUG_CONCAT")                
    #pdb.set_trace()
    #print(current_json)
    for current_index, json_data in current_json.items():
        es_content=json_data
        es_content.pop('_id', None)
        print(es_content)
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