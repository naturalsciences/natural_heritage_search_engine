import requests,json, sys
from requests.auth import HTTPBasicAuth
import dateutil
from elasticsearch import Elasticsearch

es = None
url_root = "http://collections.naturalsciences.be/cpb/nh-collections/institutions/institutions#c0=all&b_start=0"
url_suffix_collection_list = "/2-cetaf-passport-collections"
INDEX_NAME_COLLECTIONS = "cetaf_passport_collections"
INDEX_NAME_COLLECTIONS_FULL = "cetaf_passport_collections_full"
dict_inst_urls = {}
dict_collections_url = {}
dict_collections = {}
auth_mars = HTTPBasicAuth('ftheeten2021', 'ftheeten')
list_checked = []


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--user_mars")
    parser.add_argument("--password_mars")
    parser.add_argument("--es_server")
    args = parser.parse_args()
    
    es =  Elasticsearch(
        [args.es_server],       
        use_ssl = False,
        port=9200,
        timeout=30
    )
    auth_mars = HTTPBasicAuth(args.user_mars, args.password_mars)
    src_excel=args.source_excel
    get_mars_url(root_list_institutions)