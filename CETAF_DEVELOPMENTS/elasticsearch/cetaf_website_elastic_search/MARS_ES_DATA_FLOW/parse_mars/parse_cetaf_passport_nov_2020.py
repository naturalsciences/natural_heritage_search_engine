import requests,json, sys
from requests.auth import HTTPBasicAuth
import dateutil
from elasticsearch import Elasticsearch
import csv



url_root = "http://collections.naturalsciences.be/cpb/nh-collections/countries/belgium/be-rbins/"
filename="root_institution.txt"
auth_mars = HTTPBasicAuth('ftheeten', 'mamy1999')
i_cpt=1
parsed_objects=[]

def get_mars_url(p_url, p_dest):
    global i_cpt
    global parsed_objects
    with open(p_dest, 'w' , encoding="utf-8",newline='') as csvfile:
        data=requests.get(p_url, headers={'accept':'application/json'}, auth=auth_mars)
        dict=json.loads(data.text)
        writer = csv.writer(csvfile, delimiter='\t')
        writer.writerow(["field", "type", "description", "sample value"])
        for key, val in dict.items():            
            if key not in ["items", "edition_menu"]:
                print(key)
                type_v=type(val)
                print(type_v)
                try:
                    if "content-type" in val:
                        type_v=val["content-type"]
                        val=None
                except TypeError as te:
                    print(key, 'is not iterable')
                writer.writerow([key, type_v, None, val])
        children=dict["items"]
        for child in children:
            if child["@type"] not in ["Link", "Topic", "Folder", "Image", "parent"] and child["@type"] not in parsed_objects :    
                #print(child["title"])
                #print(child["@id"])
                #print(child["@type"])
                name_file=str(i_cpt)+"_"+child["@type"]+".txt"
                i_cpt+=1
                parsed_objects.append(child["@type"])
                get_mars_url(child["@id"], name_file)

if __name__ == "__main__":
    filename=str(i_cpt)+"_"+filename
    i_cpt+=1
    get_mars_url(url_root, filename)
    