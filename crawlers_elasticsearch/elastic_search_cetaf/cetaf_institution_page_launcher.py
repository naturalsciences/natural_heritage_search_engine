from cetaf_institution_page import InstitutionOrCollectionDetail
import json
from elasticsearch import Elasticsearch

endpoint="http://collections.naturalsciences.be/cpb/nh-collections/countries/belgium/be-rbins/passport/2-cetaf-passport-collections"
es_index="cetaf_registry"


Institutions={}
inst_list=[]
my_parser=InstitutionOrCollectionDetail(endpoint)
rbins_data=my_parser.get_es_json()


elastic_instance = Elasticsearch(
    ['ursidae.rbins.be'],    
    port=9200,
    use_ssl = False
)

inst_list.append(rbins_data)
Institutions["institutions"]=inst_list
elastic_instance.index(index=es_index, doc_type='document', id=endpoint, body=Institutions)