import json
from elasticsearch import Elasticsearch, helpers, exceptions

INDEX_NAME="cetaf_passport_collections_full"
INDEX_NAME_SEARCH="cetaf_passport_collections"
es=None
relations={}
complete_docs={}
complete_docs_search={}

depth_count=True
breadth_count=True
breadth_sum_area=True
breadth_sum_taxonomic_category_in_discipline=True

force_area=True
force_discipline=True
force_discipline_in_unit_count=True


max_level=0



def update_levels(base_level):
    global relations
    global max_level
    call_recurs=False
    parent={ key:value for (key,value) in relations.items() if value["level"] == base_level}
    print("========================")
    for key,val in parent.items():
        #print(key)
        #print(val)
        children={ key2:value2 for (key2,value2) in relations.items() if value2["parent"] == key}
        if len(children)>0:
            #print("has child")
            max_level=base_level+1
            call_recurs=True
            for key3, val3 in children.items():
                relations[key3]["level"]=max_level
    if call_recurs:
        print("CALL for")
        print(max_level)
        update_levels(max_level)
                

def calculate_sub_collections(parent_coll):
    global relations    
    min_mids_level=10
    max_primary_types_count=0
    max_specimens_count=0
    max_units_count=0
    tmp_owc=1
    #count itself
    tmp_cpt=relations[parent_coll]["size_and_digitisation_fields"]
    if "specimens_count" in tmp_cpt:
        max_specimens_count+=tmp_cpt["specimens_count"]
    if "units_count" in tmp_cpt:
        max_units_count+=tmp_cpt["units_count"]
    if "primary_types_count" in tmp_cpt:
        max_primary_types_count+=tmp_cpt["primary_types_count"]
    if "mids_level" in tmp_cpt:
        if tmp_cpt["primary_types_count"] <min_mids_level:
           min_mids_level=tmp_cpt["primary_types_count"]
    #count sub collections
    colls={ key:value for (key,value) in relations.items() if value["parent"] == parent_coll}    
    if len(colls.items())>0:
        for key, val in colls.items():
            print("child of "+parent_coll+ " : "+key)
            tmp_cpt=relations[key]["size_and_digitisation_fields"]
            if "specimens_count" in tmp_cpt:
                max_specimens_count+=tmp_cpt["specimens_count"]
            if "units_count" in tmp_cpt:
                max_units_count+=tmp_cpt["units_count"]
            if "primary_types_count" in tmp_cpt:
                max_primary_types_count+=tmp_cpt["primary_types_count"]
            if "mids_level" in tmp_cpt:
                if tmp_cpt["primary_types_count"] <min_mids_level:
                   min_mids_level=tmp_cpt["primary_types_count"]
        print("Max xnit found")
        print(max_units_count)
        print("Max specimens found")
        print(max_specimens_count)
        print("Max type found")
        print(max_primary_types_count)
        
    if max_units_count > 10000000:
       tmp_owc=8
    elif max_units_count > 1000000:
        tmp_owc=7
    elif max_units_count > 100000:
        tmp_owc=6
    elif max_units_count > 10000:
        tmp_owc=5
    elif max_units_count > 1000:
        tmp_owc=4
    elif max_units_count > 100:
        tmp_owc=3
    elif max_units_count > 10:
        tmp_owc=2    
    relations[parent_coll]["size_and_digitisation_fields_sum_all"]["mids_level"]= min_mids_level   
    relations[parent_coll]["size_and_digitisation_fields_sum_all"]["owc_size_evaluation"]= tmp_owc
    relations[parent_coll]["size_and_digitisation_fields_sum_all"]["primary_types_count"]= max_primary_types_count
    relations[parent_coll]["size_and_digitisation_fields_sum_all"]["specimens_count"]= max_specimens_count
    relations[parent_coll]["size_and_digitisation_fields_sum_all"]["units_count"]= max_units_count
    #if len(colls.items())>0:
    print(relations[parent_coll])    
        
def count_specimens(current_level):
    global max_level
    global relations
    global breadth_count
    global depth_count
    global breadth_sum_area
    global breadth_sum_taxonomic_category_in_discipline
    global force_area
    global force_discipline
    global force_discipline_in_unit_count 
    colls={ key:value for (key,value) in relations.items() if value["level"] == current_level}
    for key,val in colls.items():
        print(key)
        max_mids_level=0
        max_primary_types_count=0
        max_specimens_count=0
        max_unit_counts=0
        if(breadth_count):
            if breadth_sum_area:
                if "taxonomic_category" in val["taxonomic_discipline"]:
                    i_categ=0
                    name_discipline=val["taxonomic_discipline"]["taxonomic_discipline_name"]
                    #update category by area                    
                    for categ in val["taxonomic_discipline"]["taxonomic_category"]:
                        #print("INDEX CATEG "+str(i_categ))
                        #print("categ")
                        #print(categ["taxonomic_category_name"])
                        area_count=0
                        if "countries_and_areas" in categ:
                            i_area=0                            
                            for area in categ["countries_and_areas"]:
                                #print("INDEX AREA "+str(i_area))
                                #print("area found")
                                if "area_quantity" in area:
                                    #print("quantity_found")
                                    #print(area["area_quantity"])
                                    area_count+=area["area_quantity"]
                                i_area +=1
                            #print("areas sum")
                            #print(area_count)
                        update_area=True
                        if relations[key]["taxonomic_discipline"]["taxonomic_category"][i_categ] != area_count:
                            print("!!!!!! Different count for "+key + " and categ "+str(i_categ)+ " "+relations[key]["taxonomic_discipline"]["taxonomic_category"][i_categ]["taxonomic_category_name"])
                        if "taxonomic_category_quantity" in val["taxonomic_discipline"]["taxonomic_category"][i_categ] and force_area is False:
                             update_area=False                        
                        if update_area is True and area_count>0 :
                            relations[key]["taxonomic_discipline"]["taxonomic_category"][i_categ]["taxonomic_category_quantity"]= area_count
                            print("UPDATE AREA SUM "+str(area_count))                            
                        i_categ += 1
                    #sum all category in discipline
                    if breadth_sum_taxonomic_category_in_discipline:
                        i_categ=0
                        categ_sum=0                    
                        for categ in val["taxonomic_discipline"]["taxonomic_category"]:
                            if "taxonomic_category_quantity" in categ:
                                categ_sum+=categ["taxonomic_category_quantity"]
                            i_categ += 1
                        #print("SUM FOR "+name_discipline)    
                        #print(categ_sum)
                        if relations[key]["taxonomic_discipline"]["taxonomic_discipline_quantity"] !=categ_sum:
                            print("!!! Different count for "+key+ " and discipline "+name_discipline+ " "+str(categ_sum)+ " and "+str(relations[key]["taxonomic_discipline"]["taxonomic_discipline_quantity"]))
                        update_discipline=True
                        if "taxonomic_category_discipline" in relations[key]["taxonomic_discipline"] and force_discipline is False:
                            update_discipline =False
                        if update_discipline is True and categ_sum>0:
                            relations[key]["taxonomic_discipline"]["taxonomic_discipline_quantity"] = categ_sum
                            print("UPDATE CATEG SUM "+str(categ_sum))
            #sum categ in count                 
            if force_discipline_in_unit_count:
                categ_sum=0
                for categ in val["taxonomic_discipline"]["taxonomic_category"]:
                    if "taxonomic_category_quantity" in categ:
                        categ_sum+=categ["taxonomic_category_quantity"]
                if "size_and_digitisation_fields" in relations[key]:
                    if "units_count" in relations[key]["size_and_digitisation_fields"]:
                        if relations[key]["size_and_digitisation_fields"]["units_count"] != categ_sum:
                            print("! Different unit count for "+str(key)+ " : "+str(relations[key]["size_and_digitisation_fields"]["units_count"])+ " and "+str(categ_sum))
                        if categ_sum>0:
                            relations[key]["size_and_digitisation_fields"]["units_count"]=categ_sum                        
                            print("UPDATE CATEG SUM "+str(categ_sum)+ " for "+key)        
            
        #sum sub collections                
        if depth_count and current_level < max_level: 
            print("CALCULATE SUB COLLECTION FOR "+key)
            calculate_sub_collections(key)                
    if current_level > 1:
        count_specimens(current_level-1)             
  
def update_es():
    global es
    global relations
    global complete_docs
    global complete_docs_search
    global INDEX_NAME
    global INDEX_NAME_SEARCH
    for key, val in relations.items():
        print(key)
        
        size_and_digitisation_fields=val["size_and_digitisation_fields"]
        size_and_digitisation_fields_sum_all=val["size_and_digitisation_fields_sum_all"]
        taxonomic_discipline=val["taxonomic_discipline"]
        print("size_and_digitisation_fields :")
        print(size_and_digitisation_fields)
        print("size_and_digitisation_fields_sum_all :")
        print(size_and_digitisation_fields_sum_all)
        print("taxonomic_discipline :")
        print(taxonomic_discipline)        
        complete_obj=complete_docs[key]
        complete_obj["size_and_digitisation_fields"]=size_and_digitisation_fields
        complete_obj["size_and_digitisation_fields_sum_all"]=size_and_digitisation_fields_sum_all
        complete_obj["coverage_fields"]["taxonomic_discipline"]=taxonomic_discipline
        response1 = es.update(index=INDEX_NAME,  id=key, body={"doc":complete_obj})
        complete_obj_search=complete_docs_search[key]
        complete_obj_search["size_and_digitisation_fields"]=size_and_digitisation_fields
        complete_obj_search["size_and_digitisation_fields_sum_all"]=size_and_digitisation_fields_sum_all
        response2 = es.update(index=INDEX_NAME_SEARCH,  id=key, body={"doc":complete_obj_search})
        print("updated ES FOR "+key )
        
def parse():
    global es
    global relations
    global complete_docs
    global root
    es =  Elasticsearch(
        ['ursidae.rbins.be'],       
        use_ssl = False,
        port=9200,
    )
   
     # call the helpers library's scan() method to scroll
    resp_scroll = helpers.scan(
        es,
        scroll = '3m',
        size = 10,
        index=INDEX_NAME
    )

    # returns a generator object
    print (type(resp_scroll))
    for num, doc in enumerate(resp_scroll):
        print("id="+doc["_id"])
        
        taxon_discipline_main={}
        if "coverage_fields" in doc["_source"]:
            cov=doc["_source"]["coverage_fields"]
            if "taxonomic_discipline" in cov:
                taxon_discipline_main=cov["taxonomic_discipline"]
        size_main={}
        if "size_and_digitisation_fields" in doc["_source"]:
            size_main=doc["_source"]["size_and_digitisation_fields"]
        size_main_sum={}
        if "size_and_digitisation_fields_sum_all" in doc["_source"]:
            size_main_sum=doc["_source"]["size_and_digitisation_fields_sum_all"]
        tmp_elem={}
        tmp_elem["size_and_digitisation_fields"]=size_main
        tmp_elem["size_and_digitisation_fields_sum_all"]=size_main_sum
        tmp_elem["taxonomic_discipline"]=taxon_discipline_main
            
        if "to_parent_collection" in doc["_source"].keys():
            tmp_elem["level"]=-1
            tmp_elem["parent"]=doc["_source"]["to_parent_collection"]    
        else:
            tmp_elem["level"]=1
            tmp_elem["parent"]="/"
           
        relations[doc["_id"]]=tmp_elem
        complete_docs[doc["_id"]]=doc["_source"]
    #SEARCH
    resp_scroll_search = helpers.scan(
        es,
        scroll = '3m',
        size = 10,
        index=INDEX_NAME_SEARCH
    )
    for num, doc in enumerate(resp_scroll_search):
        complete_docs_search[doc["_id"]]=doc["_source"]
    #print(relations)
    
    
if __name__ == "__main__":
    # execute only if run as a script
    parse()
    update_levels(1)
    print("MAX LEVELS")
    print(max_level)
    count_specimens(max_level)
    update_es()