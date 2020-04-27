import requests
from lxml import html
from cetaf_crawler import ParsePage


class InstitutionOrCollectionDetail:
    def __init__(self, p_endpoint,p_mode="institution",  p_headers= {"Accept": "application/json","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0","Connection": "keep-alive"}):
        self.endpoint = p_endpoint
        self.headers=p_headers
        self.mode=p_mode
        self.returned={}
    
    def metadata(self):
        endpoint="http://collections.naturalsciences.be/cpb/tests/table4"
        my_parser=ParsePage(endpoint, "RBINS")
        staff_data=my_parser.get_es_json()
        self.returned['ISO3166']='BE', 
        self.returned['institution_acronym_en']='RBINS', 
        self.returned['institution_acronym']=[{'language': 'en', 'name':'RBINS'},
                                 {'language': 'nl', 'name':'KBIN'},
                                 {'language': 'fr', 'name':'IRSNB'}
                                ]
        self.returned['institution_names']=[{'language': 'en', 'name':'Royal Belgian Institute for Natural Sciences'},
                                 {'language': 'nl', 'name':'Koninklijk Belgische Instituut voor Natuurwetenschappen'},
                                 {'language': 'fr', 'name':'Institut Royal des Sciences Naturelles de Belgique'}
                                ]
        
        self.returned['metadata_url']=endpoint
        self.returned['contact']={'address': 'Vautier street, 29, 19, B-1000 Brussels',
                                  'telephone': [ '(+32) 2 627 42 38','(+32) 2 627 42 65','(+32) 2 627 42 11']}
        self.returned['director']= { 'title':'General Director a.i.','person':{'name':'Supply', 'surname':'Patricia'}, 'telephone':'+32 (0)2 627 42 69', 'mail':'directie@naturalsciences.be'}
        self.returned['head_of_collections'] ={ 'title':'Head of Scientific Service of Heritage','person':{'name':'Semal', 'surname':'Patrick'}, 'telephone':'+32 (0)2 627 43 80', 'mail':'patrick.semal@naturalsciences.be'}
        self.returned['administrative_note'] ='The Royal Belgian Institute of Natural Sciences is a Federal scientific establishment governed by the Belgian Science Policy Office (BELSPO).It is a state Service, managed by 3 independent entities: a Scientific Council; a Nature Focus Management Commission and a Management Board.'
        self.returned['collection_note']= 'RBINS has an estimated 38 million specimens in its vaults. That makes RBINS one of the ten most important natural history collections in the world, as well as the largest in Europe after Paris and London. Treasures such as the Bernissart Iguanodons, the Spy Neandertals, the Dautzenberg shell collection, the four fragments of moon rock, the thylacine (Tasmanian wolf), and Baron De Selys Longchamps’ insect collections are unique in the world. These collections, which are the result of many decades of exploration and research, help us to better understand the history of life on Earth and biodiversity, and to come up with better ways of protecting the environment. Today, with the aid of modern technology, scientists are making new discoveries about this natural heritage. The collections can be roughly divided up into six categories: entomology, recent invertebrates, recent vertebrates, anthropology, palaeontology and geology. Click on the pictures below for a more detailed overview of the collection categories, the rare specimens, the importance of collections for science and find out more about the people whose job it is to conserve these natural treasures.'
        self.returned['staff_data']=staff_data
                                
     
    def attribute_value(self, html_xml, itemprop, output_key):
        tmplist=html_xml.xpath("//td[@itemprop='"+ itemprop +"']")
        if(len(tmplist)>0):
            self.returned[output_key]=tmplist[0].text
            
            
    def assign_if_exists(self, p_json, service_key, output_key):
        if service_key in p_json:
            self.returned[output_key]=p_json[service_key]
            
    def parse_response(self, p_json):
        self.metadata()
        self.assign_if_exists(p_json, "uid","uid")
        self.assign_if_exists(p_json, "lsid","lsid")
        self.assign_if_exists(p_json, "title","title")
        self.assign_if_exists(p_json, "subjects","subjects")
        self.assign_if_exists(p_json, "total_specimens","total_specimens")
        self.assign_if_exists(p_json, "accessions__specimens_","accession_count")
        self.assign_if_exists(p_json, "primary_types","primary_types")
        self.assign_if_exists(p_json, "recorded_cards_in_database","recorded_cards_in_database")
        self.assign_if_exists(p_json, "registered_cards","registered_cards")
        self.assign_if_exists(p_json, "review_state","review_state")
        self.assign_if_exists(p_json, "scientific_visitors_per_year","scientific_visitors_per_year")
        self.assign_if_exists(p_json, "virtual_access_per_year","virtual_access_per_year")
        self.assign_if_exists(p_json, "visiting_days_per_year","visiting_days_per_year")
        self.assign_if_exists(p_json, "ontgoing_loans__parcels___specimens__per_year","ontgoing_loans_parcels_specimens_per_year")
        self.assign_if_exists(p_json, "modified","modified")
        if self.mode=="institution":
            collections=CollectionBrowser(self.endpoint)
            json_collection_list=collections.get_es_json()
            #print(json_collection_list)
            self.returned["collection_list"]=json_collection_list["collection_list"]


    def curl_connect(self):
        content = requests.get(self.endpoint, headers=self.headers)
        self.parse_response(content.json())
        
        
    def parse(self):
        self.curl_connect()
    
    def get_es_json(self):
        self.parse()
        return self.returned
        
class CollectionBrowser:
    def __init__(self, p_endpoint, p_suffix="/collections/collections", p_headers= {"Accept": "application/json","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0","Connection": "keep-alive"}):
        self.endpoint = p_endpoint + p_suffix
        self.headers=p_headers
        self.returned={}
        
    def curl_connect(self):
        print( self.endpoint)
        content = requests.get(self.endpoint, headers=self.headers)
        #print(content)
        self.browse_page(content.json())

        
    def parse(self):
        self.curl_connect()
    
    def assign_if_exists(self,coll_json_main, p_json, service_key, output_key):
        if service_key in p_json:
            coll_json_main[output_key]=p_json[service_key]
            
    def parse_details(self,coll_json_main, url):
        content = requests.get(url, headers=self.headers)
        coll_json=content.json()
        self.assign_if_exists(coll_json_main, coll_json, "abstract","abstract")
        self.assign_if_exists(coll_json_main, coll_json, "codes","codes")
        self.assign_if_exists(coll_json_main, coll_json, "collection_doi","collection_doi")
        self.assign_if_exists(coll_json_main,coll_json, "contact_email","contact_email")
        self.assign_if_exists(coll_json_main, coll_json, "contributors","contributors")
        self.assign_if_exists(coll_json_main, coll_json, "created","created")
        self.assign_if_exists(coll_json_main, coll_json, "creators","creators")
        self.assign_if_exists(coll_json_main, coll_json, "effective","effective")
        self.assign_if_exists(coll_json_main, coll_json, "metadata_language","language")
        self.assign_if_exists(coll_json_main, coll_json, "legal_property","legal_property")
        self.assign_if_exists(coll_json_main, coll_json, "lower_date","lower_date")
        self.assign_if_exists(coll_json_main, coll_json, "modified","modified")
        self.assign_if_exists(coll_json_main, coll_json, "number_of_specimens_","number_of_specimens_")
        self.assign_if_exists(coll_json_main, coll_json, "original_collectors","original_collectors")
        self.assign_if_exists(coll_json_main, coll_json, "owc_evaluation","owc_evaluation")
        self.assign_if_exists(coll_json_main, coll_json, "primary_types","primary_types")
        self.assign_if_exists(coll_json_main, coll_json, "source","source")
        self.assign_if_exists(coll_json_main, coll_json, "subjects","subjects")
        self.assign_if_exists(coll_json_main, coll_json, "taxonomic_coverage","taxonomic_coverage")
        self.assign_if_exists(coll_json_main, coll_json, "upper_date","upper_date")
        
    def browse_page(self, p_json):        
        #print(p_json)
        array_collections=[]
        batching=p_json["batching"]
        current=batching["@id"]
        next=batching["next"]
        last=batching["last"]
        go=True
        i=1
        while go and i<1000:
            items=p_json["items"]
            for coll in items:
                coll_json={}
                coll_json["url"]=coll["@id"]
                coll_json["title"]=coll["title"]
                coll_json["acronym"]=coll["description"]            
                coll_json["type"]=coll["@type"]
                self.parse_details(coll_json, coll_json["url"])
                array_collections.append(coll_json)
            self.returned["collection_list"]=array_collections
            
            p_json=requests.get(next, headers=self.headers)
            if current==last:
                go=False
                i=i+1
            else:
                current=next
                p_json=requests.get(current, headers=self.headers).json()
    
    def get_es_json(self):
        self.parse()
        return self.returned
            