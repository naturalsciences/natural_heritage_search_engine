import urllib2
import urllib
import json
from elasticsearch import Elasticsearch

import linecache
import sys
import re
#ftheeten 2018 12 19
import os
sys.path.append(os.path.abspath("../lib"))
from postgres_parser import PostgresParser

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

def camelcase_to_phrase(param):
    #https://stackoverflow.com/questions/5020906/python-convert-camel-case-to-space-delimited-using-regex-and-taking-acronyms-in
    param = re.sub(r"""
        (            # start the group
            # alternative 1
        (?<=[a-z])  # current position is preceded by a lower char
                    # (positive lookbehind: does not consume any char)
        [A-Z]       # an upper char
                    #
        |   # or
            # alternative 2
        (?<!\A)     # current position is not at the beginning of the string
                    # (negative lookbehind: does not consume any char)
        [A-Z]       # an upper char
        (?=[a-z])   # matches if next char is a lower char
                    # lookahead assertion: does not consume any char
        )           # end the group""",
    r' \1', param, flags=re.VERBOSE)
    return param



class MarsParser(PostgresParser):

    def __init__(self, p_elastic_instance, p_index_name, p_url, p_params, p_headers, p_institution, p_department,  p_collection_name ):
        self.m_url = p_url
        self.m_params = p_params
        self.m_headers = p_headers
        self.m_institution= p_institution 
        self.m_department = p_department
        self.m_collection_name = p_collection_name
        self.m_elastic_instance =  p_elastic_instance
        self.m_index_name = p_index_name
        #ftheeten 2018 12 19
        PostgresParser.__init__(self)

    def getLastPage(self, data):
        try:
            return data["batching"]["last"]
        except Exception, e:
             PrintException()

    def getNextPage(self, data):
        try:
            return data["batching"]["next"]
        except Exception, e:
             PrintException()

    def get_page_content(self, p_url, p_params, p_headers):
        try:
            request = urllib2.Request(p_url+p_params, headers=p_headers)
            contents = urllib2.urlopen(request).read()
            return contents
        except Exception, e:
             PrintException()

    def browse_and_map_items(self, data, url_json):
        try:
            for item in data['items']:
                #print(item)
                id = item["@id"]
                type = item["@type"]
                type = camelcase_to_phrase(type)
                format="HTML page"
                
                creation_date = item["creation_date"]
                modification_date = item["modification_date"]
                content = item["description"]
                title = item["title"]
                source = item["source"]
                keywords_to_add=[]
                for keyword in item["tags"]:
                    new_keyword={"keyword_value" : keyword, "keyword_type" : "tag"}
                    keywords_to_add.append(new_keyword)
                review_state={"keyword_value" : item["review_state"], "keyword_type" : "review_state"}
                keywords_to_add.append(review_state)
                
                
                content_array=[]
                content_array.append(content)
                content_array.append(title)
                
                search_to_add=[]
                #who                
                for author in item["authors"]:
                    new_people={}
                    authortmp=author["firstname"]+" "+author["lastname"]
                    new_people = {"main_category": "who", "sub_category": "author" , "value" : authortmp.strip() }
                    search_to_add.append(new_people)
                creator = item["creator"]
                creator = {"main_category": "who", "sub_category": "creator" , "value" : creator}
                search_to_add.append(creator)
                identifiers =  [{"identifier": title, "identifier_type": "title" }, {"identifier": source, "identifier_type": "source" } ]
                
                
                
                for author in item["authors"]:
                    new_people={}
                    authortmp=author["firstname"]+" "+author["lastname"]
                    new_people = {"main_category": "who", "sub_category": "author" , "value" : authortmp.strip() }
                    search_to_add.append(new_people)
                creator = item["creator"]
                creator = {"main_category": "who", "sub_category": "creator" , "value" : creator}
                search_to_add.append(creator)
                identifiers =  [{"identifier": title, "identifier_type": "title" }, {"identifier": source, "identifier_type": "source" } ]
               
                #what
                #object
                obj_json = {"main_category": "what", "sub_category": "main_object_category" , "value" : "Bibliographical entry" , "sub_category_weight": 9}
                search_to_add.append(obj_json)
                #title
                title_json = {"main_category": "what", "sub_category": "title" , "value" : title , "sub_category_weight": 9}
                search_to_add.append(title_json)
                #format
                main_format_json = {"main_category": "what", "sub_category": "format_of_document" , "value" : ["Web page", "BibTeX", "EndNote", "PDF", "RIS", "XML/MODS" ], "sub_category_weight": 8 }
                search_to_add.append(main_format_json)

                elastic_json = { "id" : id, "url" : id,  "urls_metadata": [{"url_value": url_json, "url_annex_type": "JSON webservice of MARS"}], "object_identifiers" : identifiers, "object_format" : format, "institution" : self.m_institution, "object_type": type  ,"department" : 'BE-'+self.m_institution+'-'+self.m_department, "main_collection" : 'BE-'+self.m_institution+'-'+self.m_collection_name, "content_text" : content_array, "search_criteria" : search_to_add, "other_keywords" : keywords_to_add, "data_creation_date": creation_date, "data_modification_date": modification_date}
                try: # Add to the elasticsearch instance
                #print values_to_add
                    self.m_elastic_instance.index(index=self.m_index_name, doc_type='document', id=elastic_json['id'], body=elastic_json)
                    #ftheeten 2018 12 12
                    PostgresParser.log_json_row(self, elastic_json['url'],elastic_json)
                except Exception as inst:
                    print "Error adding URL: "+elastic_json['url']
                    PrintException()
                else:
                    print "Added Article with URL "+elastic_json['url']
        except Exception, e:
             PrintException()

    def handle_mars_service(self, p_url, p_params, p_headers):
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
                self.browse_and_map_items(json_text, p_url)
        except Exception, e:
             PrintException()

    def run(self):
        try:
            self.handle_mars_service(self.m_url, self.m_params, self.m_headers)
        except Exception, e:
             PrintException()

####################### end class ###############

url="http://biblio.naturalsciences.be/@nh-search?"
params = urllib.urlencode({'type' : 'ArticleReference'})
request_headers = {
"Accept": "application/json",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Connection": "keep-alive" 
}
elasticInstance = Elasticsearch(
    ['localhost'],
    http_auth=('elastic', 'changeme'),
    port=9200,
    use_ssl=False
)
indexname="naturalheritage"



mars_parser =  MarsParser(elasticInstance, indexname, url, params, request_headers, "RBINS",  "Library", "Publications")
mars_parser.run()

