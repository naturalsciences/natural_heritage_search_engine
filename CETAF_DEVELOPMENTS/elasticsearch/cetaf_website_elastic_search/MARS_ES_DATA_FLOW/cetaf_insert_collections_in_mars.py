import pandas as pd

import requests,json
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import re
import sys
 
cols_obj={}
dict_inst_urls={}
dict_detect_duplicates={}

results={}
src_excel="Cetaf_life_collection_normalized_no_lux.xlsx"
url_root="http://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions#c0=all&b_start=0"
auth_mars=HTTPBasicAuth('', '')
url_parent_inst="http://collections.naturalsciences.be/cpb/nh-collections/countries/countries"

def test_page_exists(p_url):
    resp=requests.get(p_url, headers={'accept':'application/json'}, auth=auth_mars)
    if str(resp.status_code)=="200":
        return True
    else:
        return False
        
def get_mars_url(p_url):
    global dict_inst_urls
    data=requests.get(p_url, headers={'accept':'application/json'})
    dict=json.loads(data.text)
    go=True
    while go:
        current=dict["batching"]["@id"]
        if "next" in dict["batching"]:
            next=dict["batching"]["next"]
        last=dict["batching"]["last"]
        for inst in dict["items"]:
            print(inst["@id"])
            data2=requests.get(inst["@id"], headers={'accept':'application/json'})
            dict2=json.loads(data2.text)
            print(dict2["institution_id"])
            dict_inst_urls[dict2["institution_id"].lower()]=inst["@id"]
        if current==last:
           go=False
        else:
            print("GO NEXT" + next)
            data=requests.get(next, headers={'accept':'application/json'})
            dict=json.loads(data.text)
    print(dict_inst_urls)
    
def cast_to_int(val):
    if str(val).isdigit():
        return str(val)
    else:
        tmp=[int(s) for s in str(val).split() if s.isdigit()]
        if len(tmp)>0:
            return str(tmp[0])
        else:
            return None       
        
def coll_to_mars_acronym(p_value):
    p_value=p_value.lower()
    if p_value=="animal sound archive":
        return "dat", "Data","Other","data-oth"
    elif p_value=="arachnida":
        return "iz","Zoology Invertebrates", "Arachnids","IZ-ARA"
    elif p_value=="arthopoda (other)":
        return "iz","Zoology Invertebrates",None,"IZ-ARA-OTH"
    elif p_value=="botany":
        return "bot", "Botany", None,"BOT-GENERAL"
    elif p_value=="coleoptera":
        return "iz","Zoology Invertebrates","Insects","IZ-ENT"
    elif p_value=="diptera":
        return "iz","Zoology Invertebrates","Insects","IZ-ENT"
    elif p_value=="dna and tissue bank":
        return "mol","DNA / RNA / Tissue",None,"mol-dna"
    elif p_value=="economic botany":
        return "bot", "Botany",None,"BOT-OTH"
    elif p_value=="entomology":
        return "iz","Zoology Invertebrates","Insects","IZ-ENT"
    elif p_value=="herpetology":
        return "vz","Zoology Vertebrates" ,None,"VZ-HERP"
    elif p_value=="hymenoptera":
        return "iz","Zoology Invertebrates",None,"IZ-ENT"
    elif p_value=="ichtyology":
        return "vz","Zoology Vertebrates" ,"Fishes","VZ-PIS"
    elif p_value=="invertebrates":
        return "iz","Zoology Invertebrates",None,"IZ-GENERAL"
    elif p_value=="lepidoptera & trichoptera":
        return "iz","Zoology Invertebrates",None,"IZ-ENT"
    elif p_value=="mammalogy":
        return "vz","Zoology Vertebrates" ,"Mammals","VZ-MAM"
    elif p_value=="microscope slides":
        return "mol","DNA / RNA / Tissue", None,"MOL-TIS"
    elif p_value=="molecular and tissue samples":
        return "mol","DNA / RNA / Tissue",None,"mol-dna"
    elif p_value=="mollusca":
        return "iz","Zoology Invertebrates","Mollucs","IZ-MOL"
    elif p_value=="mycology":
        return "bot", "Botany","Fungi/Lichens","BOT-FUN"
    elif p_value=="myriapoda":
        return "iz","Zoology Invertebrates","Crustacea & myriapods","IZ-CRU"
    elif p_value=="ornithology":
        return "vz","Zoology Vertebrates" ,"Birds","VZ-AVE"
    elif p_value=="other invertebrates":
        return "iz","Zoology Invertebrates",None,"IZ-OTH"
    elif p_value=="seed":
        return "bot", "Botany","Seed plants","BOT-SEE"
    elif p_value=="tissues and dna":
        return "mol","DNA / RNA / Tissue",None,"MOL-TIS"
    elif p_value=="vertebrates":
        return "vz","Zoology Vertebrates" ,None,"VZ-GENERAL"
    elif p_value=="zoology":
        return "vz","Zoology Vertebrates" ,None,"VZ-DATA-GENERAL"
    #else:
    #    return "NOT FOUND",None,"NOT FOUND"

def create_page_logic(parent_url, current_url, json_data, type_current, type_parent, parent_title="", mode="insert"):
    print("Try to create "+current_url)
    print("parent is "+parent_url)
    print("title is "+parent_title)
    if mode=="update":
        print("UPDATE_MODE")
        print(json_data)
        imported={
              '@id':current_url, 
              "@type":type_current, 
              
              }
        imported.update(json_data)
        resp=requests.patch(current_url, json=imported, headers={'accept':'application/json'}, auth=auth_mars)
    else:
        imported={
              '@id':current_url, 
              "@type":type_current, 
               "parent":{
                "@id": parent_url,
                "review_state": "private",
                "@type": type_parent,
                
                },
               "title": parent_title
              }
        imported.update(json_data)
        resp=requests.post(imported["parent"]["@id"], json=imported, headers={'accept':'application/json'}, auth=auth_mars)
    print(resp.status_code)
    print(resp.text)

def create_collection(parent_url, json):
    super_parent=parent_url+"/2-cetaf-passport-collections"
    build_url_parent=super_parent+"/"+json["mars_parent"].lower()
    build_url_collection=build_url_parent+"/"+json["url_suffix_mars"]
    test_parent=test_page_exists(super_parent)
    json_data={}
    json_data["collection_id"]=json["id_collection_mars"]
    json_data["title"]=json["life_Typology"]
    json_data["description"]="Added_automatically from old website by python script. Original designation : "+json["life_Typology"] + " for "+ json["institution"]+" ("+json["mars_acronym"]+")"
    json_data["abstract"]="Added_automatically from old website by python script. Original designation : "+json["life_Typology"] + " for "+ json["institution"]+" ("+json["mars_acronym"]+")"
    json_data["number_of_specimens_"]=cast_to_int(json["life_individuals"])
    json_data["primary_types"]=cast_to_int(json["life_type"])
    json_data["other_size_indicator"]="Life pc card :"+ str(json["life_pc_cards"])+". Life pc recorded : "+str(json["life_pc_recorded"])
    test_parent=test_page_exists(super_parent)
    if test_parent:
        print("parent exists for "+json["life_Typology"]+ " : "+  super_parent )
    else:
        print("parent doesn't exist for "+json["life_Typology"] + " : "+super_parent)
        parent_val={"title":json["label_mars_parent"], "description":"Added automatically by python script to allow adding of subcollections"}
        create_page_logic( super_parent, build_url_parent, parent_val, "cetaf_passport_collections","collection_institution","" )
    test_parent2=test_page_exists(build_url_parent)
    if test_parent2:
        print("parent2 (main collection) exists for "+json["life_Typology"]+ " : "+  build_url_parent )
    else:
        print("parent2 (main collection) doesn't exist for "+json["life_Typology"] + " : "+build_url_parent)
        parent_val={ "description":"Added automatically by python script to allow adding of subcollections"}
        create_page_logic( super_parent, build_url_parent, parent_val, "Folder", "cetaf_passport_collections",json["mars_parent"])                
    
    test_url=test_page_exists(build_url_collection)
    if test_url:
        print("UDPATE page exists for "+json["life_Typology"])
        create_page_logic( build_url_parent, build_url_collection, json_data, "nh_collection", "Folder",json["life_Typology"], "update")
    else:
        print("page to be created for "+json["life_Typology"])
        create_page_logic( build_url_parent, build_url_collection, json_data, "nh_collection", "Folder",json["life_Typology"])
       
def parse(excel):
    global results
    global dict_inst_urls
    global dict_detect_duplicates
    print(excel)
    ex_data = pd.read_excel(excel)
    headers=ex_data.head()
    current_inst=None
    i=0
    for cols in ex_data.columns:
        #print(cols)
        cols_obj.update({i:cols})
        i+=1
    for i, row in ex_data.iterrows():
        #print(i)
        if not row[3] is None:
            key=str(row[1])+"/"+str(row[3])   
            val={}
            val['id_collection_mars']=key
            for key2, col_name in cols_obj.items():
                val[col_name]=row[key2]
            #print(row[3].lower())
            key_mars, label_mars_parent, name_col_mars, url_part=coll_to_mars_acronym(str(row[3]).lower())
            url_part=url_part.lower()
            val["mars_parent"]=key_mars
            val["label_mars_parent"]=label_mars_parent
            val["name_col_mars"]=name_col_mars
            val["url_suffix_mars"]=url_part
            if name_col_mars is None:
                val["name_col_mars"]=row[3]
            
            if val["mars_acronym"].lower() in dict_inst_urls:
                parent_url=dict_inst_urls[val["mars_acronym"].lower()]            
                test_parent=test_page_exists(parent_url)
                if test_parent:
                    #print(val["mars_acronym"]+ "exists : "+ parent_url)
                    key_coll= val["mars_acronym"].lower()+"/"+url_part
                    if key_coll in dict_detect_duplicates:
                        print("!! DUPLICATE FOR "+ key_coll)
                        key_dup=dict_detect_duplicates[key_coll]["cpt"]
                        key_dup=key_dup+1
                        #key_coll=key_coll+"-"+str(key_dup)
                        dict_detect_duplicates[key_coll]["cpt"]=key_dup
                        val["url_suffix_mars"]=url_part+"-"+str(key_dup)
                        print("New suffix : "+val["url_suffix_mars"] )
                    else:
                        dict_detect_duplicates[key_coll]={"cpt":0}
                else:
                   print(val["mars_acronym"]+ "DOESN'T EXIST : "+ parent_url)
            else:
                print(val["mars_acronym"].lower()+ " NOT FOUND" )
            create_collection(parent_url, val)
            results.update({key:val})
            
            '''
            results[current_inst].update({'name':current_inst})
            for key, col_name in cols_obj.items():
                  print(key)
                  print(col_name)
                  print(row[key])
            '''
      
if __name__ == "__main__":
    get_mars_url(url_root)
    parse(src_excel)
    #print(results)