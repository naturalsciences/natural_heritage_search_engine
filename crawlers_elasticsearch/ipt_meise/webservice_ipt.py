import urllib2
import urllib
import requests
import zipfile
import json
from elasticsearch import Elasticsearch
import io
import StringIO

import linecache
import sys
import re
import csv

import calendar
import datetime

csv.field_size_limit(5000000)

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
	
def WriteException(p_log_file):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    p_log_file.write('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    p_log_file.write("\n")
	
def removeduplicate(array):
    return[json.loads(y) for y in list(set([json.dumps(x).encode('utf-8') for x in array]))]

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

def null_if_empty(var):
    if isinstance(var, (int, long, float, complex)):
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
    
class IPTParser(object):

    def __init__(self, p_elastic_instance, p_index_name, p_url, p_dataset_name, p_headers, p_institution, p_department,  p_collection_name, p_logfile ):
        self.m_url = p_url
        self.m_dataset_name = p_dataset_name
        self.m_headers = p_headers
        self.m_institution= p_institution 
        self.m_department = p_department
        self.m_collection_name = p_collection_name
        self.m_elastic_instance =  p_elastic_instance
        self.m_index_name = p_index_name
        self.m_logfile = p_logfile
        
    def parse_and_insert_item(self, item, url_specimen):
        try:
            search_criterias=[]
            what = []
            format = "Web page"
            #type/collection
            type_object=[ camelcase_to_phrase(item["preparations"]), "Botanical specimen" ]
            
        
            for type in type_object :
                main_type_json = {"main_category": "what", "sub_category": "main_object_category" , "value": type, "sub_category_weight": 10 }
                search_criterias.append(main_type_json)
            main_format_json = {"main_category": "what", "sub_category": "format_of_document" , "value" : format, "sub_category_weight": 9 }
            search_criterias.append(main_format_json)
            #id
            identifiers=[]
            identifiers.append({"identifier": item["catalogNumber"], "identifier_type": "specimen number" })
            if(len(empty_if_null(item['scientificName']))>0):
                identifiers.append({"identifier": item["scientificName"], "identifier_type": "biological scientific name" })
            if(len(empty_if_null(item['typeStatus']))>0):
                identifiers.append({"identifier": item["typeStatus"], "identifier_type": "biological type status" })
				
            identifier_json= {"main_category": "what", "sub_category": "object_number" , "value" : item["catalogNumber"], "sub_category_weight": 7 }
            #zoological type
            search_criterias.append(identifier_json)
            type_json= {"main_category": "what", "sub_category": "biological_type_status" , "value" : item['typeStatus'], "sub_category_weight": 6 }
            
            #taxon
            taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['kingdom'] , "sub_category_weight": 8.8, "rank": "pylum"}
            search_criterias.append(taxon_json)
            what.append(item['kingdom'])
            taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['phylum'] , "sub_category_weight": 8.7, "rank" : "kingdom"}
            search_criterias.append(taxon_json)
            what.append(item['phylum'])
            taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['class'] , "sub_category_weight": 8.6, "rank" : "class"}
            search_criterias.append(taxon_json)
            what.append(item['class'])
            taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['order'] , "sub_category_weight": 8.5, "rank" :"order"}
            search_criterias.append(taxon_json)
            what.append(item['order'] )
            taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['family'] , "sub_category_weight": 8.4, "rank" : "family"}
            search_criterias.append(taxon_json)
            what.append(item['family'])
            taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['genus'] , "sub_category_weight": 8.3, "rank" : "genus"}
            search_criterias.append(taxon_json)
            what.append(item['genus'])
            taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['scientificName'] , "sub_category_weight": 8.2}
            search_criterias.append(taxon_json)
            what.append(item['scientificName'])
            taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['acceptedNameUsage'] , "sub_category_weight": 8.1}
            search_criterias.append(taxon_json)
            what.append(item['acceptedNameUsage'] )
            
            
            #collector
            collector = {"main_category": "who", "sub_category": "collector" , "value" : item['recordedBy'] }
            search_criterias.append(collector)
            
            #collecting date
            #not catching all formats of Meise
            date_from = None
            date_to = None
            when=[]
            if(len(empty_if_null(item['year']))>0):
                date_from =item['year']
                date_to = item['year']
                if(len(empty_if_null(item['month']))>0):
                    month =item['month'].zfill(2)
                    date_from  = date_from +'-'+month
                    date_to  = date_to +'-'+month
                    if(len(empty_if_null(item['day']))>0):
                        day =item['day'].zfill(2)
                        date_from  = date_from +'-'+day
                        date_to  = date_to +'-'+day
                    else:
                        date_from  = date_from +'-01'
                        last_day_of_month= calendar.monthrange(int(item['year']),int(item['month']))[1]
                        date_to  = date_to +'-' + str(last_day_of_month).zfill(2)
                else :
                    date_from = date_from + '-01-01'
                    date_to = date_to + '-12-31'
                
                
                when.append({"date_type": "collecting_date" , "date_begin" : date_from, "date_end" : date_to})
            
            
            #country
            if(len(empty_if_null(item['country']))>0):
                new_geo_country = {"main_category": "where", "sub_category": 'country' , "value" :item['country'] }
                what.append(item['country'])
                search_criterias.append(new_geo_country)
            if(len(empty_if_null(item['countryCode']))>0):
                iso_country = {"main_category": "where", "sub_category": 'ISO_3166-2_country_code' , "value" : item['countryCode'], 'hide_in_facets':false }
                search_criterias.append(iso_country)
            #locality & habitat
            if(len(empty_if_null(item['locality']))>0):
                locality = {"main_category": "where", "sub_category": 'exact_site' , "value" :item['locality'] }
                what.append(item['locality'])
                search_criterias.append(locality)
            
            if(len(empty_if_null(item['habitat']))>0):
                habitat = {"main_category": "where", "sub_category": 'natural_site' , "value" :item['habitat'] }
                what.append(item['habitat'])
                search_criterias.append(habitat)
            if(len(empty_if_null(item['locationRemarks']))>0):
                locality_remarks = {"main_category": "where", "sub_category": "other_geographical_element" , "value" : item['locationRemarks'] }  
                search_criterias.append(locality_remarks)
            
            #coordinates
            latitude= item['decimalLatitude']
            longitude = item['decimalLongitude']
            coordinates=[]
            if latitude is not None and longitude is not None:
                if(len(empty_if_null(latitude))>0 and len(empty_if_null(longitude))>0) :
                    coordinates.append({"geo_ref_point" :{'lat': latitude  ,'lon':    longitude} })
            
            #ipr
            license = item['license']
            if(len(empty_if_null(license))>0):
                license_json = {"main_category": "attribution_and_user_rights", "sub_category": "license" , "value" : license }  
                search_criterias.append(license_json)
            right_holder = item['rightsHolder']
            if(len(empty_if_null(right_holder))>0):
                right_json = {"main_category": "attribution_and_user_rights", "sub_category": "right_holder" , "value" : right_holder }  
                search_criterias.append(right_json)
                
                
            #last modification
            last_modification= item["modified"]
            #if(len(empty_if_null(last_modification))>0):
            #    print(last_modification)
            #    last_modification=datetime.datetime.strptime(last_modification, '%m/%d/%y' ).strftime( '%Y-%m-%d')
            
            elastic_json= { "id" : null_if_empty(url_specimen), "url" : null_if_empty(url_specimen),     "urls_metadata": [{"url_annex_type": "IPT webservice"}], "object_identifiers" : identifiers, "object_format" : format, "institution" : self.m_institution, "object_type": type_object    ,"department" : 'BE-'+self.m_institution+'-'+self.m_department, "main_collection" :  'BE-'+self.m_institution+'-'+self.m_collection_name, "content_text" : null_if_empty(removeduplicate(what)), "search_criteria" : null_if_empty(removeduplicate(search_criterias)), "dates": when, "data_creation_date": null_if_empty(last_modification), "data_modification_date": null_if_empty(last_modification)}
            if len(coordinates)>0: 
                elastic_json["coordinates"] = coordinates
            #print(elastic_json)
            self.m_elastic_instance.index(index=self.m_index_name, doc_type='document', id=elastic_json['id'], body=elastic_json)
        except Exception as inst:
            print "Error adding URL: "+url_specimen
            self.m_logfile.write( "Error adding URL: "+url_specimen + "\n")
            WriteException(self.m_logfile)
            self.m_logfile.write("value:\n")
            self.m_logfile.write(json.dumps(elastic_json))
            self.m_logfile.write("\n")
        else:
            print "Added Article with URL "+elastic_json['url']

    def parse_occurrences(self, occ_file, name):
        try:
            datastream = StringIO.StringIO(occ_file.read(name))
            reader = csv.DictReader(datastream, delimiter='\t')
            print(reader.fieldnames)
            for row in reader:
                try:
                    print(row['id'])
                    self.parse_and_insert_item(row, row['id'])
                except Exception:
                    PrintException()            
        except Exception:
            PrintException()

    def handle_ipt_service(self, p_url, p_dataset):
        try:        
            print("debug")
            u = urllib.urlopen(p_url + p_dataset)
            print(p_url + p_dataset)
            print(u)
            tmp=io.BytesIO(u.read())
            zip_handler = zipfile.ZipFile(tmp, 'r')
            print(zip_handler.infolist())
            print(zip_handler.namelist())
            return zip_handler
            #return {name: zip_handler.read(name) for name in zip_handler.namelist()}
        except Exception:
             PrintException()

    def run(self):
        try:
            zip_handler = self.handle_ipt_service(self.m_url, self.m_dataset_name)
            #print(files['occurrence.txt'])
            #occ = files['occurrence.txt']
            tmp =self.parse_occurrences(zip_handler, "occurrence.txt")
        except Exception:
             PrintException()


####################### end class ###############        
        
#url="http://biocase.africamuseum.be/ipt_rmca/"
#url= url+"archive.do?r="
url="http://apm-ipt.br.fgov.be:8080/ipt-2.3.5/"
url= url+"archive.do?r="

dataset_name = "botanical_collection"
params = urllib.urlencode({'type' : 'ArticleReference'})
elasticInstance = Elasticsearch(
    ['localhost'],    
    port=9200,
    use_ssl=False
)
indexname="naturalheritage"
logfile = open('meise_parsing.log', 'w')

ipt_parser =  IPTParser(elasticInstance, indexname, url, dataset_name, None, "Meise Botanic Garden",  "Herbarium Collection", "Herbarium Collection", logfile)
ipt_parser.run()


close(logfile)