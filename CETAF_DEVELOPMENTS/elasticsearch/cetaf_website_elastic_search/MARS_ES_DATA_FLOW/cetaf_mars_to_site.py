import requests,json
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import re
import csv
import sys

es=None
url="http://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions#c0=all&b_start=0"
INDEX_NAME_INSTITUTIONS="cetaf_passport_institutions"
INDEX_NAME_INSTITUTIONS_FULL="cetaf_passport_institutions_full"
output_file="output_cetaf.txt"

dict_inst={}

def find_by_item_prop(html_elem, prop, soup):
    returned=""
    node=soup.find(html_elem, itemprop=prop)
    if node:
        returned=node.get_text(strip=True)
    return returned
    
def get_address(p_url):
    dict={}
    data=requests.get(p_url, headers={'accept':'application/json'})
    dict=json.loads(data.text)
    clean = re.compile('<.*?>')
    if "address" in dict:
        print("ADDRESS=")
        print(dict["address"])
        address=dict["address"]["data"]
        address=address.replace("<strong>","")
        address=address.replace("</strong>","")
        address=address.replace("\r","")
        address=address.replace("\n","")
        address=address.replace("\t","")
        print(address)
        soup = BeautifulSoup(address, 'html.parser')
        country_val=""
        city_val=""
        street_val=""
        postcode_val=""
        
        try:
            '''        
            country_val = str(soup.find('td', text = "Country:").findNext("td").contents[0])
            city_val = str(soup.find('td', text = "City:").findNext("td").contents[0])
            street_val = str(str(soup.find('td', text = "Street:").findNext("td").contents[0]))
            postcode_val = str(soup.find('td', text = "Post Code:").findNext("td").contents[0])
            '''
            country_val=find_by_item_prop("td", "country", soup)
            city_val=find_by_item_prop("td", "city", soup)
            street_val=find_by_item_prop("td", "street", soup)
            postcode_val=find_by_item_prop("td", "postcode", soup)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            
        country_val=re.sub(clean,'', country_val)
        city_val=re.sub(clean,'', city_val)
        street_val=re.sub(clean,'', street_val)
        print(postcode_val)
        print(type(postcode_val))
        postcode_val=re.sub(clean,'', postcode_val)
        print(country_val)
        print(city_val)
        return {'country':country_val, 'city': city_val, 'street':street_val, 'postcode':postcode_val }

def get_institution(p_url):    
    global dict_inst
    dict={}
    data=requests.get(p_url, headers={'accept':'application/json'})
    dict=json.loads(data.text)
    name=dict["title"]
    wikidata_id=dict["wikidata_id"]
    institution_id=dict["institution_id"]
    grscicoll_code=dict["grscicoll_code"]
    grid_id=dict["grid_id"]
    description=""
    if "description" in dict:
        description=dict["description"]
    country=dict["parent"]["title"]
    print(name)
    print(country)
    address_url=p_url+"/1-cetaf-passport-administration"
    address=get_address(address_url)
    dict_inst[institution_id]={"name":name, "country":country, "institution_id": institution_id , "grscicoll_code":grscicoll_code, "grid_id": grid_id, "wikidata_id": wikidata_id, "description":description, "address":address}
    
    

def parse(p_url):
    dict={}
    print(p_url)
    data=requests.get(p_url, headers={'accept':'application/json'})
    print(data.text)
    dict=json.loads(data.text)
    go=True
    while go:
        current=dict["batching"]["@id"]
        if "next" in dict["batching"]:
            next=dict["batching"]["next"]
        last=dict["batching"]["last"]
        for inst in dict["items"]:
            print(inst["@id"])
            get_institution(inst["@id"])
        if current==last:
           go=False
        else:
            print("GO NEXT" + next)
            data=requests.get(next, headers={'accept':'application/json'})
            dict=json.loads(data.text)

def insert_es():
    global dict_inst
    global INDEX_NAME_INSTITUTIONS
    global INDEX_NAME_INSTITUTIONS_FULL
    global es
    for key, data in dict_inst.items():
        print(key)
        print(data)
        to_write={}
        to_write["url_id"]=data["institution_id"]
        to_write["full_path"]=data["institution_id"]
        to_write["institution_name"]=data["name"]
        identification={}
        identification["unique_acronym"]=data["institution_id"]
        identification["grscicoll_code"]=data["grscicoll_code"]
        identification["wikidata_id"]=data["wikidata_id"]
        identification["grid_id"]=data["grid_id"]
        to_write["identification_fields"]=identification
        address_tmp=data["address"]
        institution_address={}
        if not address_tmp is None:
            institution_address={"country": data["country"], "city":address_tmp["city"], "street":address_tmp["street"], "postcode":address_tmp["postcode"]}
        print(institution_address)
        to_write["institution_address"]=institution_address
        to_write["institution_description"]=data["description"]
        es.index(index=INDEX_NAME_INSTITUTIONS, doc_type= "_doc",id=to_write["identification_fields"]["unique_acronym"], body=to_write)
        es.index(index=INDEX_NAME_INSTITUTIONS_FULL, doc_type= "_doc",id=to_write["identification_fields"]["unique_acronym"], body=to_write)
        
def write_file(p_file):
    global dict_es
    csv_columns=["name", "country", "institution_id",  "grscicoll_code", "grid_id", "wikidata_id", "description", "address"]
    with open(p_file, 'w', encoding="utf-8",newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter='\t')
        writer.writeheader()
        for val in dict_inst.items():
            print(val[1])
            writer.writerow(val[1])    
            
if __name__ == "__main__":
    es =  Elasticsearch(
        ['ursidae.rbins.be'],       
        use_ssl = False,
        port=9200,
    )
    parse(url)
    #insert_es()
    write_file(output_file)