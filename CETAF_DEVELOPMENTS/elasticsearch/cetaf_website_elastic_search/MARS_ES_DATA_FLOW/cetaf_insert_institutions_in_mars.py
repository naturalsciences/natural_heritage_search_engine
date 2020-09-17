import pandas as pd
import requests,json
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
import re
import sys

cols_obj={}
dict={}
dict_inst={}
results={}
src_excel="C:\\Users\\ftheeten\\Downloads\\CETAF_institutions_GrSciColl_Mars_code.xlsx"
url_root="http://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions#c0=all&b_start=0"
auth_mars=HTTPBasicAuth('USER', 'PASSWORD')

#reference assignation moifyng parameters
def assign_if_in_data(global_updated, field_name, mars_variable , data_row, force=False):
    if len(mars_variable.strip())==0:
        if field_name in data_row:
            tmp= data_row[field_name]
            if len(tmp)>0 or force:
                mars_variable=tmp
                global_updated=True
                print("UPDATED SET TO TRUE")
    return [global_updated, mars_variable]

def write_html_address(country='', city='', postcode='', street='', phone='', mail=''):
     return '<h6>&nbsp;</h6>\r\n\r\n<table border="0" cellpadding="1" cellspacing="1" style="width:800px">\r\n\t<tbody>\r\n\t\t<tr>\r\n\t\t\t<td style="width:100px"><strong>Street:</strong></td>\r\n\t\t\t<td itemprop="street">'+ street +'</td>\r\n\t\t</tr>\r\n\t\t<tr>\r\n\t\t\t<td style="width:100px"><strong>City:</strong></td>\r\n\t\t\t<td itemprop="city">'+ city +'</td>\r\n\t\t</tr>\r\n\t\t<tr>\r\n\t\t\t<td><strong>Post Code:</strong></td>\r\n\t\t\t<td itemprop="postcode">'+postcode+'</td>\r\n\t\t</tr>\r\n\t\t<tr>\r\n\t\t\t<td>Country</td>\r\n\t\t\t<td itemprop="country">'+country+'</td>\r\n\t\t</tr>\r\n\t\t<tr>\r\n\t\t\t<td><strong>Phone:</strong></td>\r\n\t\t\t<td itemprop="phone">'+phone+'</td>\r\n\t\t</tr>\r\n\t\t<tr>\r\n\t\t\t<td><strong>e-mail:</strong></td>\r\n\t\t\t<td itemprop="mail"><a href="mailto:'+mail+'">'+mail+' </a></td>\r\n\t\t</tr>\r\n\t</tbody>\r\n</table>\r\n\r\n<p>&nbsp;</p>\r\n'    
                
def insert_mars_logic(p_url, p_code):
    global results
    global auth_mars
    if p_code in results:
        data_row=results[p_code]   
        data_row={k.lower():v for k,v in data_row.items() }        
        print(p_url)
        adm_url=p_url+'/1-cetaf-passport-administration'
        data=requests.get(adm_url, headers={'accept':'application/json'})
        dict_address=json.loads(data.text)
        clean = re.compile('<.*?>')
        if "address" in dict_address:
            
            print("HAS_ADDRESS")
            print(dict_address["address"])
            address_original=dict_address["address"]["data"]
            address=dict_address["address"]["data"]
            address=address.replace("<strong>","")
            address=address.replace("</strong>","")
            address=address.replace("\r","")
            address=address.replace("\n","")
            address=address.replace("\t","")
            
            soup = BeautifulSoup(address, 'html.parser')
            country_val=""
            city_val=""
            street_val=""
            postcode_val=""
            phone_val=""
            email_val=""
            try:
                country_val = str(soup.find('td', text = "Country:").findNext("td").contents[0])
                city_val = str(soup.find('td', text = "City:").findNext("td").contents[0])
                street_val = str(str(soup.find('td', text = "Street:").findNext("td").contents[0]))
                postcode_val = str(soup.find('td', text = "Post Code:").findNext("td").contents[0])
                phone_val = str(soup.find('td', text = "Phone:").findNext("td").contents[0])
                email_val = str(soup.find('td', text = "e-mail:").findNext("td").contents[0])
            except:
                print("Unexpected error:", sys.exc_info()[0])
            
            country_val=re.sub(clean,'', country_val)
            city_val=re.sub(clean,'', city_val)
            street_val=re.sub(clean,'', street_val)
            postcode_val=re.sub(clean,'', postcode_val)
            phone_val=re.sub(clean,'', phone_val)
            email_val=re.sub(clean,'', email_val)
            
            print("COUNTRY :" + country_val )
            print("city_val :" + city_val )
            print("street_val :" + street_val )
            print("postcode_val :" + postcode_val )
            
            force=True
            updated=False
            updated, country_val=assign_if_in_data(updated, "country", country_val,data_row, force)
            updated, city_val=assign_if_in_data(updated, "city", city_val,data_row, force)
            updated, street_val=assign_if_in_data(updated, "street", street_val,data_row, force)
            updated, postcode_val=assign_if_in_data(updated, "postalcode", postcode_val,data_row, force)
            updated, phone_val=assign_if_in_data(updated, "phone", phone_val,data_row, force)
            updated, email_val=assign_if_in_data(updated, "email", email_val,data_row, force)
            if updated==True or force:
                print("UPDATED COUNTRY : "+country_val)
                print("UPDATED CITY : "+city_val)
                print("UPDATED STREET : "+street_val)
                print("UPDATED POSTCODE : "+postcode_val)
                html_address=write_html_address(country_val,city_val, postcode_val, street_val, phone_val, email_val)
                print(html_address)
                resp=requests.patch(adm_url, json={'address':{'data':html_address}}, headers={'accept':'application/json'}, auth=auth_mars)
                print(resp.status_code)
            else:
                print("ORIGINAL COUNTRY : "+country_val)
                print("ORIGINAL CITY : "+city_val)
                print("ORIGINAL STREET : "+street_val)
                print("ORIGINAL POSTCODE : "+postcode_val)
        else:
            print("HAS_NO_ADDRESS")
        
def insert_mars():
    global results
    for key, data in results.items():
        print(data['mars_code'])
        code=data['mars_code'].lower()
        if code in dict_inst:
           print("Found :"+code )
           work_url=dict_inst[code]["url"]
           insert_mars_logic(work_url, code)
        else:
           print("Not found :"+code )
           
def add_or_concatenate_key(row, institution, pos, field):
    global results
    if not pd.isna(row[pos]):
        existing=""
        if field in results[institution]:            
            existing=results[institution][field]
            print("EXISTING "+field + " in "+institution+"="+existing)
            existing=existing+"\r\n"+str(row[pos])
        else:
            print("NEW "+field + " in "+institution+"="+str(row[pos]))
            existing=str(row[pos])
        results[institution].update({field:str(existing).strip()})

def parse(excel):
    global results
    print(excel)
    ex_data = pd.read_excel(excel)
    headers=ex_data.head()
    current_inst=""
    i=0
    for cols in ex_data.columns:
        print(cols)
        cols_obj.update({i:cols})
        i+=1
    for i, row in ex_data.iterrows():
        print(i)
        if not pd.isna(row[0]):
            current_inst=row[1].lower() #mars_code
            results.update({current_inst:{}})
        print(current_inst)
        
        results[current_inst].update({'name':current_inst})
        for key, col_name in cols_obj.items():
              print(key)
              print(col_name)
              print(row[key])
              add_or_concatenate_key(row, current_inst, key, col_name)
    #print(results)
    
def get_institution(p_url):    
    global dict_inst
    dict={}
    data=requests.get(p_url, headers={'accept':'application/json'})
    dict=json.loads(data.text)
    name=dict["title"]
    wikidata_id=dict["wikidata_id"]
    institution_id=dict["institution_id"].lower()
    grscicoll_code=dict["grscicoll_code"]
    grid_id=dict["grid_id"]
    description=""
    if "description" in dict:
        description=dict["description"]
    country=dict["parent"]["title"]
    print(name)
    print(country)
    dict_inst[institution_id]={"name":name, "country":country, "institution_id": institution_id , "grscicoll_code":grscicoll_code, "grid_id": grid_id, "wikidata_id": wikidata_id, "description":description, "url":p_url}

def parse_mars(p_url):
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
            
if __name__ == "__main__":
    parse(src_excel)
    parse_mars(url_root)
    insert_mars()
    #print(results)