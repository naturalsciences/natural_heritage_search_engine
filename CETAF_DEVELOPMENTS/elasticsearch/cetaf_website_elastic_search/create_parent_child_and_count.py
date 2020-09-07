import json
from elasticsearch import Elasticsearch, helpers, exceptions

INDEX_NAME="cetaf_passport_collections_full"
es=None
relations={}
root=[]

def add_in_relation(index, id_parent, id_child, array_col):
    if id_parent in index:
        tmp=index[id_parent]
        tmp[id_child]=array_col
        index[id_parent]=tmp
    else:
        tmp={}
        tmp[id_child]=array_col
        index[id_parent]=tmp
    return index
    
def update_levels():
    global relations
    global root
    for root_col in root:
        print("root_col "+root_col)
        tmp_idx=relations["/"]
        for key in tmp_idx[root_col]:
             print("sub_col "+key)
             val=tmp_idx[root_col][key]
             print(val) 
        
def parse():
    global es
    global relations
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
        
        taxon_discipline_main=None
        if "coverage_fields" in doc["_source"]:
            cov=doc["_source"]["coverage_fields"]
            if "taxonomic_discipline" in cov:
                taxon_discipline_main=cov["taxonomic_discipline"]
        size_main=None
        if "size_and_digitisation_fields" in doc["_source"]:
            size_main=doc["_source"]["size_and_digitisation_fields"]
        
        if "to_parent_collection" in doc["_source"].keys():
            id_parent=doc["_source"]["to_parent_collection"]
            tmp_elem={}
            tmp_elem["size_and_digitisation_fields"]=size_main
            tmp_elem["taxonomic_discipline"]=taxon_discipline_main
            tmp_elem["level"]=-1
            relations=add_in_relation(relations,id_parent,doc["_id"],tmp_elem)                   
        else:
            print("has no parent")
            tmp_root={}
            tmp_root["size_and_digitisation_fields"]=size_main
            tmp_root["taxonomic_discipline"]=taxon_discipline_main
            tmp_root["level"]=1            
            relations=add_in_relation(relations,"/",doc["_id"],tmp_root)      
            root.append(doc["_id"])

    print(relations)
    
if __name__ == "__main__":
    # execute only if run as a script
    parse()
    update_levels()