import json
from elasticsearch import Elasticsearch, helpers, exceptions

INDEX_NAME="cetaf_passport"
es=None
relations={}

def parse():
    global es
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
        print (doc["_id"])
        query_child= {
            "query":{
              "parent_id": {
              "type": "root",
              "id": doc["_id"]
               }
            }
        }
        result_children = es.search(index=INDEX_NAME, body=query_child)
        relations[doc["_id"]]=[]
        for hit in result_children["hits"]["hits"]:
            print(" CHILD:"+hit["_id"])
            relations[doc["_id"]].append(hit["_id"])
            #upd_body={
            #          "script":{
            #                "source":"ctx._source.direct_children.add(params.child)",
            #                "params" : {
            #                    "child" : hit["_id"]
            #                    }
            #                }
            #         }
            #response = es.update(index=INDEX_NAME,  id=doc["_id"], body=upd_body)
    print(relations)
    for key, nested in relations.items():
        for child in nested:
            print(key+"=>"+child)
            upd_body={"doc":{"direct_children":nested}}
            response = es.update(index=INDEX_NAME,  id=key, body=upd_body)
        """
        print(key)
        print(nested)
        """
if __name__ == "__main__":
    # execute only if run as a script
    parse()
