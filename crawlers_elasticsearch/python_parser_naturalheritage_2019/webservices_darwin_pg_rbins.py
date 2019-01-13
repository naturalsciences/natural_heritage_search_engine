#python 3.4
import urllib
import json
from elasticsearch import Elasticsearch
import requests
from requests.auth import HTTPBasicAuth

import datetime
import psycopg2
import psycopg2.extras
import linecache
import sys
import json
import argparse
import re
#ftheeten 2018 12 19
import os
sys.path.append(os.path.abspath("lib"))
from postgres_parser import PostgresParser
import imp
#2019 01 08
from elasticsearch import Urllib3HttpConnection, Elasticsearch

'''
class MyConnection(Urllib3HttpConnection):
    def __init__(self, *args, **kwargs):
        extra_headers = kwargs.pop('extra_headers', {})
        super(MyConnection, self).__init__(*args, **kwargs)
        self.headers.update({'Content-Type': 'application/json'})
'''


def removeduplicate(array):
    returned=[]
    for elem in array:
        if not elem  in returned:
            returned.append(elem)       
    return returned

def null_if_empty(var):
    if isinstance(var, (int, float, complex)):
        return var
    if var is None:
        return None
    if isinstance(var, str):
        if len(var.replace("\n","").replace("\r",""))==0:
            return None
    if len(var)==0:
        return None
    return var
    
def empty_if_null(var):
    if var is None:
        return ""
    return var

def PrintException(p_logfile):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    p_logfile.write('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    p_logfile.write('\n')


class DarwinParser(PostgresParser):

    def __init__(self, p_elastic_instance, p_index_name, p_url, p_params, p_headers, p_institution, p_department, p_parent_collection, p_collection, p_logfile ):
        self.m_url = p_url
        self.m_params = p_params
        self.m_headers = p_headers
        self.m_institution= p_institution 
        self.m_department = p_department
        self.m_parent_collection = p_parent_collection
        self.m_collection = p_collection
        self.m_elastic_instance =  p_elastic_instance
        self.m_index_name = p_index_name
        self.m_go_database = False
        self.m_logfile = p_logfile
        self.re_remove_repetition = re.compile('(.+[^0-9]+)(\d*)$')
        #ftheeten 2018 12 19
        PostgresParser.__init__(self)
        
    def set_pg_connection(self, p_connection_string, p_prefix_json="http://darwin.naturalsciences.be/search/view/id/", p_prefix_json_metadata="http://darwin.naturalsciences.be/public.php/json/getjson?id="):
        try:
            self.m_connection_string= p_connection_string
            self.m_conn = psycopg2.connect(self.m_connection_string)
            self.m_prefix_json = p_prefix_json
            self.m_prefix_json_metadata = p_prefix_json_metadata
            self.m_go_database = True
        except Exception as e:
            PrintException(self.m_logfile)
        

    def getLastPage(self, data):
        try:
            return data["last_url"]
        except Exception as e:
             PrintException(self.m_logfile)

    def getNextPage(self, data):
        try:
            return data["next_url"]
        except Exception as e:
             PrintException(self.m_logfile)

    def get_page_content(self, p_url, p_params, p_headers):
        try:
            request = urllib2.Request(p_url+p_params, headers=p_headers)
            contents = urllib2.urlopen(request).read()
            return contents
        except Exception as e:
             PrintException(self.m_logfile)
             
    def get_darwin_id_pg(self):
        try:
            query="SELECT DISTINCT id FROM specimens;"
            if not self.m_collection is  None :
                query=query+" WHERE collection_name=%s " 
            cur = self.m_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            if not self.m_collection is  None :
                print("NO_COLLECTION")
                cur.execute(query, (self.m_prefix_json, self.m_collection)    )
            else: 
                print("COLLECTION")
                cur.execute(query, [self.m_prefix_json]  )
            for item in cur:
                #print("LOOP")
                #print(item['id'])
                self.get_page_content_pg(item['id'])
        except Exception as e:
             print("EXCEPTION")
             PrintException(self.m_logfile)
             
    def get_page_content_pg(self, p_id):
        try:
            #print("TRY_DB")
            query="""SELECT distinct  specimens.id as id, 
            %s||specimens.id as public_url, collection_name, collection_code,
            parent_collection.code as parent_collection_code,
            parent_collection.name as parent_collection_name,
            (SELECT modification_date_time FROM users_tracking where referenced_relation='specimens' and record_id= max(specimens.id)     GROUP BY modification_date_time ,users_tracking.id having users_tracking.id=max(users_tracking.id) limit 1) as last_modification, code_display, string_agg(DISTINCT taxon_path::varchar, '|') as taxon_paths, string_agg(DISTINCT taxon_ref::varchar, '|') as taxon_ref,
                    string_agg(DISTINCT taxon_name, '|') as taxon_name,
                    string_agg(DISTINCT     history, '|') as history_identification
                    ,
                     string_agg(DISTINCT gtu_country_tag_value, '|') as country,  string_agg(DISTINCT gtu_others_tag_value, '|') as geographical,           
                    fct_mask_date(gtu_from_date,
                    gtu_from_date_mask) as date_from_display,
                    fct_mask_date(gtu_to_date,
                    gtu_to_date_mask) as date_to_display,
                    coll_type,                                 
                    
                    longitude, latitude
                    ,count(*) OVER() AS full_count,collector_ids, 
                    (SELECT string_agg(formated_name, '|') from people where id = any(collector_ids)) as collectors
                    , donator_ids,
                    (SELECT array_agg(formated_name) from people where id = any(donator_ids)) as donators
                    ,
                    string_agg(distinct tag_locality, '| ') as localities ,

COALESCE(jsonb_object_agg(COALESCE(specimen_comments_notion,''), COALESCE(specimen_comments,'')) FILTER (WHERE specimen_comments_notion IS NOT NULL), '[]')  as specimen_comments,
COALESCE(jsonb_object_agg(COALESCE(gtu_comments_notion,''),COALESCE(gtu_comments,'')) FILTER (WHERE gtu_comments_notion IS NOT NULL), '[]') as gtu_comments
                       
                    FROM 
                    (SELECT specimens.id,
                    collections.code as collection_code, collections.name as collection_name, 
                   (regexp_matches(collection_path||collection_ref::varchar||'/','\/(\d+)\/'))[1]::int as parent_collection_ref, COALESCE(codes.code_prefix,'')||COALESCE(codes.code_prefix_separator,'')||COALESCE(codes.code,'')||COALESCE(codes.code_suffix_separator,'')||COALESCE(codes.code_suffix,'') as code_display, full_code_indexed, taxon_path, taxon_ref, collection_ref , gtu_country_tag_indexed , gtu_country_tag_value, 
                    gtu_others_tag_indexed as localities_indexed,
                    gtu_others_tag_value
                    , taxon_name,
                    spec_coll_ids as collector_ids , 
                    spec_don_sel_ids as donator_ids,
                    gtu_from_date,
                    gtu_from_date_mask,
                    gtu_to_date,
                    gtu_to_date_mask,
                    type as coll_type,
                    case
                    when gtu_country_tag_indexed is not null then
                    unnest(gtu_country_tag_indexed) 
                    else null end
                    as country_unnest,

                    gtu_location[0] as latitude,
                    gtu_location[1] as longitude,
                    notion_date as identification_date, 
                    notion_date_mask as identification_date_mask,
                    coalesce(fct_mask_date(notion_date, notion_date_mask)||': ','')||taxon_name as history,
                     specimens.gtu_ref,
                    group_type, sub_group_type,
                    tag
                    , group_type||' -x- '||sub_group_type||' -:- '||tag as tag_locality ,

   c_specimens.notion_concerned as specimen_comments_notion,                 
c_specimens.comment as specimen_comments,
   c_gtu.notion_concerned as gtu_comments_notion, 
c_gtu.comment as gtu_comments
                    
                    FROM specimens
                    LEFT JOIN
                    collections ON
                    specimens.collection_ref=collections.id                    
                    LEFT JOIN 
                    codes
                    ON codes.referenced_relation='specimens' and code_category='main' and specimens.id=codes.record_id

                    LEFT JOIN comments c_specimens
                    ON specimens.id = c_specimens.record_id and c_specimens.referenced_relation = 'specimens'

                    LEFT JOIN comments c_gtu
                    ON specimens.gtu_ref = c_gtu.record_id and c_gtu.referenced_relation = 'gtu'

 
                    
                    LEFT JOIN identifications
                    on identifications.referenced_relation='specimens'
                    and specimens.id= identifications.record_id
                    and identifications.notion_concerned='taxonomy'
                    LEFT JOIN tags
                    ON specimens.gtu_ref=tags.gtu_ref                   
                    ) as specimens
                    LEFT JOIN
                    collections as parent_collection ON
                    parent_collection_ref=parent_collection.id
                    WHERE specimens.id=%s                
                    GROUP BY    
                    specimens.id,
                    collection_name,
                    collection_code,
                    parent_collection_name,
                    parent_collection_code,
                    code_display         
                    ,
                    gtu_from_date,
                    gtu_from_date_mask,
                    gtu_to_date,
                    gtu_to_date_mask,
                    coll_type
                    , 
                    longitude, latitude
                     ,
                     collector_ids
                      , donator_ids ;"""
            cur = self.m_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute(query, (self.m_prefix_json,  p_id))
            for item in cur:
                #print("LOOP")
                url_specimen= self.m_prefix_json + item['code_display']
                self.parse_and_insert_item(item, url_specimen)
        except Exception as e:
             print("EXCEPTION")
             PrintException(self.m_logfile)

    def parse_specimen(self, url_specimen, p_headers):
        try:
            request = urllib2.Request(url_specimen, headers = p_headers)
            contents_tmp = urllib2.urlopen(request).read()
            contents= json.loads(contents_tmp)
            for item in contents:
                self.parse_and_insert_item(item, url_specimen)
        except Exception as e:
            PrintException(self.m_logfile)
            
    def parse_and_insert_item(self, item, url_specimen):
        try:
            type_object="Natural sciences specimen"
            id_tech = str(item["id"])
            public_url= item["public_url"]
            #print(public_url)
            coll_type = item["coll_type"]
            specimen_code = item["code_display"]
            collection_name = item["collection_name"]
            collection_code = item["collection_code"]
            #ftheeten 2018 12 20
            parent_collection_name = item["parent_collection_name"]
            parent_collection_code = item["parent_collection_code"]
            taxon_names = empty_if_null(item["taxon_name"]).split("|")
            history_identification = empty_if_null(item["history_identification"]).split("|")
            collectors = empty_if_null(item['collectors']).split("|")
            donators = empty_if_null(item['collectors']).split("|")
            #print(collectors)
            #Geographical
            countries = empty_if_null(item["country"]).split("|")
            geographicals = empty_if_null(item["geographical"]).split("|")
            localities = empty_if_null(item['localities']).split("|")
            
            #2019 01 08
            #print(item["specimen_comments"])            
            specimen_comments = empty_if_null(item["specimen_comments"])
            #print(item["gtu_comments"])            
            gtu_comments = empty_if_null(item["gtu_comments"])
            
            latitude= item['latitude']
            longitude = item['longitude']
            #Date
            date_from_display = item["date_from_display"]
            #print(date_from_display)
            year_from = date_from_display[:4]
            #print(year_from)
            if(year_from=="xxxx"):
                year_from=""
            date_to_display = item["date_to_display"]
            #print(date_to_display)
            year_to = date_to_display[:4]
            #print(year_to)
            if(year_to=="xxxx"):
                year_to=""
            if(len(year_to)>0):
                date_range = date_from_display + " to " + date_to_display
            else:
                date_range = date_from_display
            #print(date_range)
            
            #multimedia
            ##remove duplicates
            
                


                
                            
            last_modification = item["last_modification"]

            #treatments
            search_criterias=[]
            format = "Web page"
            type = "Natural history collection specimen"
            main_type_json = {"main_category": "what", "sub_category": "main_object_category" , "value": type, "sub_category_weight": 10 }
            search_criterias.append(main_type_json)
            main_format_json = {"main_category": "what", "sub_category": "format_of_document" , "value" : format, "sub_category_weight": 9 }
            search_criterias.append(main_format_json)
           
                
            what = []
            for taxon_name in taxon_names:
                taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : taxon_name , "sub_category_weight": 8}
                search_criterias.append(taxon_json)
                what.append(taxon_name)
            for history_identification_elem in history_identification:
                history_json = {"main_category": "what", "sub_category": "history_of_object" , "value" : history_identification_elem, "sub_category_weight": 4 }
                search_criterias.append(history_json)
                what.append("History identification : " +    history_identification_elem)
            if len(empty_if_null(coll_type))>0:
                type_json = {"main_category": "what", "sub_category": "zoological_type_status" , "value" : coll_type, "sub_category_weight": 6 }
                search_criterias.append(type_json)
                what.append(coll_type)
                         
            keywords=[]
            keywords.append({"keyword_value" : coll_type , "keyword_type" : "Zoological type"})
            #keywords.append(taxon_name)
            #keywords.append(country)
            #keywords.append(geographical)
            date_object_begin = None
            date_object_end = None
            date_object_text = date_range
            if(len(empty_if_null(year_from))>0):
                date_object_begin = year_from + "-01-01"
            if(len(empty_if_null(year_to))>0):
                date_object_end = year_to + "-12-31"
                
            
            url_json=self.m_prefix_json_metadata+id_tech
            identifiers=[]
            identifiers =  [{"identifier": specimen_code, "identifier_type": "specimen number" },  {"identifier":  coll_type, "identifier_type": "Zoological type status"} ]
            identifier_json= {"main_category": "what", "sub_category": "object_number" , "value" : specimen_code, "sub_category_weight": 7 }
            search_criterias.append(identifier_json)
            
             #for taxon_name in taxon_names:
            #    identifiers.append({"identifier": taxon_name, "identifier_type": "scientific name (zoological)"})
            #format = "Web page"
            #type = "Zoological specimen"
            
            #WHO
            for collector in collectors:
                    new_people = {"main_category": "who", "sub_category": "collector" , "value" : collector.strip() }
                    search_criterias.append(new_people)
            for donator in donators:
                    new_people = {"main_category": "who", "sub_category": "donator" , "value" : donator.strip() }
                    search_criterias.append(new_people)
            #WHERE
            for country in countries:
                new_geo_country = {"main_category": "where", "sub_category": "country" , "value" : country.strip() }
                what.append(country.strip())
                search_criterias.append(new_geo_country)
            for locality in localities:
                items = empty_if_null(locality).split(" -:- ")
                if len(items)==2 :
                    type_loc = empty_if_null(items[0]).split(' -x- ')
                    if len(type_loc) == 2:
                        sub_category = type_loc[1].strip().lower().replace(" ", "_").strip("_")
                        #new_locality_geo = {"main_category": "where", "sub_category": type_loc[1].strip().lower().replace(" ", "_") , "value" : items[1].strip() }
                    else:
                        sub_category = items[0].strip().lower().replace(" ", "_").strip("_")
                    tmp_sub_category= self.re_remove_repetition.match(sub_category)
                    if not (tmp_sub_category is None):
                        sub_category = tmp_sub_category.group(1).strip().strip("_")
                    new_locality_geo = {"main_category": "where", "sub_category": sub_category , "value" : items[1].strip() }
                    search_criterias.append(new_locality_geo)
                    what.append(items[1].strip())
                else:
                    new_locality_geo = {"main_category": "where", "sub_category": "other geographical element" , "value" : locality }                     
            new_geo_geographical = {"main_category": "where", "sub_category": "country" , "value" : country.strip() }
            search_criterias.append(new_geo_country)
            coordinates=[]
            if latitude is not None and longitude is not None:
                coordinates.append({"geo_ref_point" :{'lat': latitude  ,'lon':    longitude} })
            #WHEN
            when=[]
            when.append({"date_type": "collecting_date" , "date_begin" : date_object_begin, "date_end" : date_object_end})

            #ftheeten 2018 12 20
            if null_if_empty(self.m_parent_collection) is None:                
                parent_collection_to_insert = parent_collection_name
            else:
                parent_collection_to_insert= self.m_parent_collection
            #ftheeten 2018 12 20
            if null_if_empty(self.m_collection) is None:              
                collection_to_insert = collection_name
            else:
                collection_to_insert = self.m_collection

            #2019 01 08
            if len(specimen_comments)>0:
                #json_specimen_comments = json.loads(specimen_comments)
                json_specimen_comments = specimen_comments
                for comment, value in json_specimen_comments.items():
                    type_json = {"main_category": "what", "sub_category": comment, "value" : value, "sub_category_weight": 2 }
                    search_criterias.append(type_json)
                    what.append(coll_type)
            
               
            if len(gtu_comments)>0:               
                #json_gtu_comments = json.loads(gtu_comments)
                json_gtu_comments = gtu_comments
                for comment, value in json_gtu_comments.items():
                    type_json = {"main_category": "where", "sub_category": comment, "value" : value, "sub_category_weight": 2 }
                    search_criterias.append(type_json)
                    what.append(coll_type)                
            
            search_criterias = filter( lambda x : len(x['value']) > 0 , search_criterias)
            '''
            print(null_if_empty(public_url))
            print(null_if_empty(url_json))
            print(identifiers)
            print(format)
            print(self.m_institution)
            print(type)
            print(self.m_institution)
            print(self.m_department)
            print(parent_collection_to_insert)
            print(collection_to_insert)
            '''
            what= removeduplicate(what)
            if last_modification is not None:
               last_modification = last_modification.isoformat()
            elastic_json= { "id" : null_if_empty(public_url), "url" : null_if_empty(public_url),     "urls_metadata": [{"url_value": url_json, "url_annex_type": "Darwin JSON webservice"}], "object_identifiers" : identifiers, "object_format" : format, "institution" : self.m_institution, "object_type": type    ,"department" : 'BE-'+self.m_institution+'-'+self.m_department, "main_collection" :  'BE-'+self.m_institution+'-'+parent_collection_to_insert,   "sub_collection": 'BE-'+self.m_institution+'-'+collection_to_insert , "content_text" : null_if_empty(what), "search_criteria" : null_if_empty(removeduplicate(search_criterias)), "dates": when, "data_creation_date":  last_modification, "data_modification_date": last_modification}
            if len(coordinates)>0: 
                elastic_json["coordinates"] = coordinates
            #print(elastic_json)    
            #self.m_elastic_instance.index(index=self.m_index_name, doc_type='document', id=elastic_json['id'], body=elastic_json)
            query_url = self.m_elastic_instance + "/" + "document"   
            
            #.replace("/","\/").replace(":","\:")
            #print(query_url)
            r= requests.post(query_url, params={'id':  (elastic_json['id']), 'op_type': 'index'}, json=elastic_json, auth=('USER', 'PASSWORD'), headers={'Content-Type': 'application/json'})
            #print(r.status_code)
            #print(r.text)
            if r.status_code >= 400:
                raise Exception('Wrong HTTP REPLY : \n '+ str(r.status_code) + '\n' + r.text)         
            #ftheeten 2018 12 12
            PostgresParser.log_json_row(self, elastic_json['url'],elastic_json)
        except Exception as inst:
            print("Error adding URL: "+url_specimen)
            self.m_logfile.write("Error adding URL: "+url_specimen)
            self.m_logfile.write('\n')
            PrintException(self.m_logfile)
            self.m_logfile.write("value:\n")
            self.m_logfile.write(json.dumps(elastic_json))
            self.m_logfile.write("\n")
        #else:
        #    print("Added Article with URL "+elastic_json['url'])
        
    

    def browse_and_map_items(self, data):
        try:
            for item in data['records']:
                url_specimen=item['url_specimen']
                print(url_specimen)
                self.parse_specimen(url_specimen, self.m_headers)
        except Exception as e:
             PrintException(self.m_logfile)

    def handle_darwin_service(self, p_url, p_params, p_headers):
        try:        
            last_page="-1"
            next_page="1"
            while(last_page!=next_page):
                contents=self.get_page_content(p_url, p_params, p_headers)
                json_text=json.loads(contents)
                last_page=self.getLastPage(json_text)
                print(last_page)
                next_page=self.getNextPage(json_text)
                print(next_page)
                p_url=next_page
                p_params=""
                self.browse_and_map_items(json_text)
        except Exception as e:
             PrintException(self.m_logfile)

    def run(self):
        try:
            print("a")
            if not self.m_go_database:
                print("b")
                self.handle_darwin_service(self.m_url, self.m_params, self.m_headers)
            else:
                print("c")
                #self.get_page_content_pg()
                self.get_darwin_id_pg()
        except Exception as e:
             PrintException(self.m_logfile)

####################### end class ###############


parser = argparse.ArgumentParser(description='Darwin parser')
parser.add_argument("-i","--institution",  help="institution", default="RMCA")
parser.add_argument("-pc","--parent_collection",  help="name of parent collection")
parser.add_argument("-cc","--collection_code",  help="collection_code")
parser.add_argument("-cn", "--collection_name", help="collection_name")
args=parser.parse_args()
logfile = open('main.log', 'w+')
url="http://193.190.223.58/public.php/search/getcollectionjson?"



#collection_code='"MAMMA_RMCA"'
#collection_code='INSECTA_TYPES_DIGIT03'
#parent_collection='Vertebrates'
#collection_name='Ichtyology'

institution = args.institution
collection_code = args.collection_code
parent_collection = args.parent_collection
collection_name = args.collection_name


print("PARSING FINISHED")



params = urllib.parse.urlencode({'collection' :  collection_code})
request_headers = {
"Accept": "application/json",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0| WOW64| rv:40.0) Gecko/20100101 Firefox/40.0",
"Connection": "keep-alive" 
}

es_server = 'http://193.190.223.60:80/'
indexname="naturalheritage"
es_server= es_server + indexname

#elasticInstance = requests.get(es_server, auth=HTTPBasicAuth('USER', 'PASSWORD'), headers={'Content-Type': 'application/json'})


darwin_parser =     DarwinParser(es_server, indexname, url, params, request_headers, institution, "Collections Management",parent_collection, collection_name, logfile )
darwin_parser.set_pg_connection("host='localhost' dbname='darwin2' user='user' password='password'")
darwin_parser.run()


