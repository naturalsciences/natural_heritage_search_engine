import requests,json, sys, collections, argparse
from requests.auth import HTTPBasicAuth
from transfer_mars_lib import remove_html, get_value_field, cast_to_numeric, cast_to_int
from elasticsearch import Elasticsearch
import copy

es=None
create_es=False

root_list_institutions="https://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions"
url_suffix_collection="/2-cetaf-passport-collections/collections/collections"
url_suffix_geo="/collection_geography"
url_suffix_mids="/list-mids"
search_index="cetaf_passport_collections"
data_index="cetaf_passport_collections_full"
es_server_name=None
current_institution_name=""
current_institution_url=""
check_date=None
check_date_default="2021-01-01T00:00:00+02:00"
all_arrays={}
parent_children={}



def get_mids(p_url, es_content_full, auth_mars):
    print("MIDS_URL")
    print(p_url)
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    mids_geography_category = get_value_field(p_dict,"mids_geography_category")
    mids_geography_mids_0 = get_value_field(p_dict,"mids-geography_mids_0")
    mids_geography_mids_1 = get_value_field(p_dict,"mids-geography_mids_1")
    mids_geography_mids_2 = get_value_field(p_dict,"mids-geography_mids_2")
    mids_geography_mids_3 = get_value_field(p_dict,"mids-geography_mids_3")
    mids_quantity = get_value_field(p_dict,"mids-geography_object_quantity")
    if not mids_quantity is None:       
        mids={}
        #TEMP
        mids["taxonomic_category_name"]=es_content_full["coverage_fields"]["main_category"]
        mids["taxonomic_category_title"]=es_content_full["coverage_fields"]["main_category"]
        mids["countries_and_areas"]=[] 
        tmp_ctry={}        
        tmp_ctry["area_type"]="TDWG Zone"
        tmp_ctry["area_name"]=mids_geography_category
        mids["countries_and_areas"].append(tmp_ctry)
        mids["taxonomic_category_quantity"]=mids_quantity
        mids["taxonomic_category_mids_0_pc"]=mids_geography_mids_0
        mids["taxonomic_category_mids_1_pc"]=mids_geography_mids_1
        mids["taxonomic_category_mids_2_pc"]=mids_geography_mids_2
        mids["taxonomic_category_mids_3_pc"]=mids_geography_mids_3
        es_content_full["coverage_fields"]["taxonomic_discipline"]["taxonomic_category"].append(mids)
        return mids_geography_category, mids_quantity, mids_geography_mids_0, mids_geography_mids_1, mids_geography_mids_2, mids_geography_mids_3



def explore_mids(p_url, es_content_full, auth_mars):
    global url_suffix_mids
    url_mids=p_url+url_suffix_mids
    print("MIDS_EXPLORE_URL")
    print(url_mids)
    data=requests.get(url_mids, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    print(p_dict)
    sum_mids={}
    if "items" in p_dict:
        for item in p_dict["items"]:
            print(item)
            if "@type" in item:
                if item["@type"]=="collection_mids_geography":
                    url=item["@id"]
                    mids_geography_category, mids_quantity, mids_geography_mids_0, mids_geography_mids_1, mids_geography_mids_2, mids_geography_mids_3 = get_mids(url, es_content_full, auth_mars)
                    #print("mids_quantity")
                    #print(mids_quantity)
                    #print(cast_to_int(mids_quantity))
                    sum_tmp={}
                    sum_tmp["quantity"]=cast_to_int(mids_quantity)
                    sum_tmp["mids_0"]=cast_to_numeric(mids_geography_mids_0)
                    sum_tmp["mids_1"]=cast_to_numeric(mids_geography_mids_1)
                    sum_tmp["mids_2"]=cast_to_numeric(mids_geography_mids_2)
                    sum_tmp["mids_3"]=cast_to_numeric(mids_geography_mids_3)
                    print("SUM_TMP")
                    print(sum_tmp)
                    sum_mids[url]=sum_tmp
    #sum
    sum=0
    sum_mids0=0
    sum_mids1=0
    sum_mids2=0
    sum_mids3=0
    for key, sum_elem in sum_mids.items():
        sum += sum_elem["quantity"]
        sum_mids0+=sum_elem["mids_0"]/100*sum_elem["quantity"]
        sum_mids1+=sum_elem["mids_1"]/100*sum_elem["quantity"]
        sum_mids2+=sum_elem["mids_2"]/100*sum_elem["quantity"]
        sum_mids3+=sum_elem["mids_3"]/100*sum_elem["quantity"]
    es_content_full["coverage_fields"]["taxonomic_discipline"]["sum_quantity"]=sum
    if sum !=0:
        es_content_full["coverage_fields"]["taxonomic_discipline"]["sum_mids_0"]=round((float(sum_mids0)/float(sum))*100,3)
        es_content_full["coverage_fields"]["taxonomic_discipline"]["sum_mids_1"]=round((float(sum_mids1)/float(sum))*100,3)
        es_content_full["coverage_fields"]["taxonomic_discipline"]["sum_mids_2"]=round((float(sum_mids2)/float(sum))*100,3)
        es_content_full["coverage_fields"]["taxonomic_discipline"]["sum_mids_3"]=round((float(sum_mids3)/float(sum))*100,3)
    
def add_collection_es(index_name, current_id,  es_content):
    #global es
    es.update(index=index_name,id=current_id,body={'doc': es_content,'doc_as_upsert':True})

def find_parent(child_id):
    global parent_children
    for key, items in parent_children.items():
        for item in items:
            if item==child_id:
                return key
    return None  
    
def explore_sub_collection_detail(p_url, p_dict,parent_url, auth_mars):
    global parent_children
    current_json={}
    print(p_dict)
    if parent_url in parent_children:
        tmp=parent_children[parent_url]
    else:
        tmp=[]
    tmp.append(p_url)
    parent_children[parent_url]=tmp
    copy_collection(p_url, p_dict, auth_mars, True)

def explore_sub_collection(p_url, parent_url, auth):
    global check_date
    #print(p_url)
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    if "modified" in p_dict:
        modified=p_dict["modified"]
        if modified>check_date:
            #print("UPDATE!!!")
            #print(modified)
            explore_sub_collection_detail(p_url, p_dict, parent_url, auth)
    

def parse_sub_collection_index(p_dict, elem, parent_url, auth_mars):
    if elem in p_dict:
        #print("INDEX")
        #print(p_dict[elem])
        for item in p_dict[elem]:
            item_type=item["@type"]
            coll_url=item["@id"]
            print("TEST="+coll_url)
            if item_type=="nh_sub_collection":
                print("SUB_COLLECTION")
                print(coll_url)
                explore_sub_collection(coll_url, parent_url, auth_mars)
 
def get_geography(p_url, auth_mars):
    print("URL_GEO=")
    print(p_url)
    returned=[]    
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    #print(p_dict)
    if "countries" in p_dict:
        if not p_dict["countries"] is None:
            if isinstance(p_dict["countries"], list):
                for item in sorted(p_dict["countries"]):
                    returned.append(item)
    return returned        
    
    
def copy_collection(p_url, p_dict, auth_mars, sub_collection=False):
    global es
    global search_index
    global data_index
    global current_institution_name
    global current_institution_url
    global all_arrays
    global parent_children
    global url_suffix_geo
    print("------------------------")
    print("FILL_URL")
    print(p_url)
    print("------------------------")
    json_parent=None
    current_json={}
    current_json_full={}
    current_json["coverage_fields"]={}
    current_json["coverage_fields"]["countries_and_areas"]=[]
    current_json["size_and_digitisation_fields"]={}
    
    current_id=p_url
    
    current_json["institution_name"]=current_institution_name
    current_json["to_parent_institution"]=current_institution_url
    
    name_collection=get_value_field(p_dict, "description")
    
    
    size_collection=get_value_field(p_dict, "number_of_specimens_")
    if not size_collection is None:
        current_json["size_and_digitisation_fields"]["specimens_count"]=size_collection
    
    #after child explore=> geo
    if not name_collection is None:
        if sub_collection:
            url_parent=find_parent(p_url)
            print("URL_PARENT=")
            print(url_parent)
            json_parent=all_arrays[url_parent]
            current_json["coverage_fields"]["main_category"]=json_parent["coverage_fields"]["main_category"]
            current_json["coverage_fields"]["taxonomic_discipline"]=name_collection
        else:
            current_json["coverage_fields"]["main_category"]=name_collection
            current_json["coverage_fields"]["taxonomic_discipline"]="Main collection"
    areas={}
    areas=get_geography(p_url+url_suffix_geo, auth_mars)
    for area in areas:
        print(area)
        new_area={}
        new_area["area_name"]=area
        current_json["coverage_fields"]["countries_and_areas"].append(new_area)
    all_arrays[p_url]=current_json
    parse_sub_collection_index(p_dict, "items", p_url, auth_mars)
    es_content=current_json
    
    add_collection_es(search_index, current_id,es_content)
    es_content_full=copy.deepcopy(es_content)
    
    #es_content_full["coverage_fields"].pop("taxonomic_discipline", None)
    #es_content_full["coverage_fields"]["taxonomic_discipline"]={}
    #GOOD ?
    es_content_full["coverage_fields"]["name_taxonomic_category"]=name_collection
    abstract=get_value_field(p_dict, "abstract")
    es_content_full["collection_abstract"]=abstract
    description=get_value_field(p_dict, "description")
    es_content_full["collection_description"]=description
    
    types=get_value_field(p_dict, "primary_types")
    es_content_full["size_and_digitisation_fields"]["primary_types_count"]=types
    
    units=get_value_field(p_dict, "number_of_units")
    es_content_full["size_and_digitisation_fields"]["units_count"]=units
    
    others=get_value_field(p_dict, "other_size_indicator")
    es_content_full["size_and_digitisation_fields"]["other_size_indicators"]=others
    
    owc=get_value_field(p_dict, "owc_evaluation")
    es_content_full["size_and_digitisation_fields"]["owc_size_evaluation"]=owc
    es_content_full["coverage_fields"].pop("taxonomic_discipline", None)
    es_content_full["coverage_fields"]["taxonomic_discipline"]={}
    es_content_full["coverage_fields"]["taxonomic_discipline"]["taxonomic_category"]=[]
    explore_mids(p_url, es_content_full, auth_mars)
    print("ES_CONTENT_FULL===>")
    print(es_content_full)
    add_collection_es(data_index, current_id,es_content_full)
    #es.update(index=search_index,id=current_id,body={'doc': es_content,'doc_as_upsert':True})

def get_collection(p_url, auth_mars):
    print(p_url)
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    #print(dict)
    not_null_id=p_dict["collection_id"]
    print("collection_name")
    print(not_null_id)
    if not not_null_id is None:
        print("PARSE___!")
        copy_collection(p_url,p_dict, auth_mars )
    
def parse_collections(p_url, auth_mars):
    print("collection list:")
    print(p_url)
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    list_collections=p_dict["items"]
    print(list_collections)
    for item in list_collections:
        print(item)
        if item["@type"]=="nh_collection":
            print("go")
            get_collection(item["@id"], auth_mars)

    

#def parse_institution_detail(p_url):
#    parse_collections(p_url)

def parse_institution(p_url, auth_mars):
    global url_suffix_collection
    global current_institution_name
    global current_institution_url
    current_institution_name=""
    current_institution_url=""
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)

    name_museum=p_dict["title"]
    print(name_museum)
    if not name_museum is None:
       if len(name_museum.lower().strip())>0:
            current_institution_name=name_museum
            current_institution_url=p_dict["@id"]
    parse_collections(p_url+url_suffix_collection, auth_mars)
   
def get_collections(p_url, auth_mars):
    data=requests.get(p_url, headers={'accept':'application/json', 'Accept-Charset':'iso-8859-1'}, auth=auth_mars)
    p_dict=json.loads(data.text)
    go=True
    i=0
    while go:
        current=p_dict["batching"]["@id"]
        if "next" in p_dict["batching"]:
            next=p_dict["batching"]["next"]
        last=p_dict["batching"]["last"]
        
        for inst in p_dict["items"]:
            print(i)
            #print(inst["@id"])
            data2=requests.get(inst["@id"], headers={'accept':'application/json'}, auth=auth_mars)
            dict2=json.loads(data2.text)
            if "institution_id" in dict2:
                #print("IS_MUSEUM")
                parse_institution( inst["@id"], auth_mars)
                i=i+1
        if current==last:
           go=False
        else:
            #print("GO NEXT" + next)
            data=requests.get(next, headers={'accept':'application/json'}, auth=auth_mars)
            p_dict=json.loads(data.text)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--es_server")
    parser.add_argument("--check_date", default=check_date_default)
    parser.add_argument("--user_mars")
    parser.add_argument("--password_mars")
    
    args = parser.parse_args()
    check_date=args.check_date
    print(check_date)
    print(args.es_server)
    es =  Elasticsearch(
        [args.es_server],       
        use_ssl = False,
        port=9200,
        timeout=30
    )
    #get_collections(root_list_institutions)
    auth_mars = HTTPBasicAuth(args.user_mars, args.password_mars)
    get_collections(root_list_institutions, auth_mars)
    #parse_institution("https://collections.naturalsciences.be/cpb/nh-collections/countries/germany/de-zfmk", auth_mars)