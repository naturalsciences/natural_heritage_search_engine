from cetaf_crawler import ParsePage
import json
from elasticsearch import Elasticsearch

endpoint="http://collections.naturalsciences.be/cpb/tests/table4"
es_index="cetaf_registry"
print(endpoint)

my_parser=ParsePage(endpoint, "RBINS")
staff_data=my_parser.get_es_json()
print(staff_data)
full_json={'institution_acronym_en':'RBINS', 
            'institution_acronyms': 
                                [{'language': 'en', 'name':'RBINS'},
                                 {'language': 'nl', 'name':'KBIN'},
                                 {'language': 'fr', 'name':'IRSNB'}
                                ],
            'institution_names': [{'language': 'en', 'name':'Royal Belgian Institute for Natural Sciences'},
                                 {'language': 'nl', 'name':'Koninklijk Belgische Instituut voor Natuurwetenschappen'},
                                 {'language': 'fr', 'name':'Institut Royal des Sciences Naturelles de Belgique'}
                                ]
                                ,
            'metadata_url': endpoint,
            'staff_data':staff_data
                                }
print(full_json)

elastic_instance = Elasticsearch(
    ['ursidae.rbins.be'],    
    port=9200,
    use_ssl = False
)
elastic_instance.index(index=es_index, doc_type='document', id=endpoint, body=full_json)