#PYTHON 3 VERSION
import ipt_parser_rbins_params as params

#import urllib2
import urllib
import requests
import zipfile
import json
from elasticsearch import Elasticsearch
import io
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3

import linecache
import sys
import re
import csv
import chardet

import calendar
import datetime
import dateutil.parser as dateparser


import sys
# sys.setdefaultencoding() does not exist in Python 3
#reload(sys)  # Reload does the trick!
#sys.setdefaultencoding('UTF8')


csv.field_size_limit(5000000)

def conv_row(row):    
    yield {key.encode(params.ENCODING).strip():value.encode(params.ENCODING).strip() for key, value in row.iteritems()}
    #row = pickle.dumps(row).encode('ascii', 'strict')
    #return pickle.loads(row.decode('ascii', 'strict'))

    
def parse_date_darwin_core_logic(date, mode="begin"):
    returned = {}
    array_date = re.compile("-|/|\s").split(date)
    year=""
    month=""
    day=""
   
    if len(array_date[0])==4:
        year=array_date[0]
        if len(array_date)>=2:
             month = array_date[1]
        if len(array_date)>=3:
             day = array_date[2]
    elif len(array_date[-1])==4:
        year = array_date[-1]
        if len(array_date)>=2:
             month = array_date[-2]
        if len(array_date)>=3:
             day = array_date[-3]
    returned['day'] = day
    returned['month'] = month 
    returned['year'] = year 
    return returned
    
def parse_date_darwin_core(date):
    returned = {}
    date=date.strip()
    if len(date)>0:
        if date.find("-")>=0:             
            date_array_prep = date.split("-")
            if len(date_array_prep) ==2 :
                if len(date_array_prep[0].strip())==4 and len(date_array_prep[1].strip())==4 :         
                    date = str.replace("-", "/")
        if date.find("-")>=0 and date.find("/")>=0:           
            date_array = date.split("/")
            if(len(date_array)) ==2:
                begin_date = date_array[0]
                end_date = date_array[1]                
                begin_date = parse_date_darwin_core_logic(begin_date)
                end_date = parse_date_darwin_core_logic(end_date)
        elif  date.find("/")>=0 and len(date.strip())==9 :           
            date_array = date.split("/")
            if(len(date_array)) ==2:
                begin_date = {}
                begin_date['year'] = date_array[0]
                begin_date['month'] = '01'
                begin_date['day'] = '01'
                end_date = {}
                end_date['year'] = date_array[1]
                end_date['month'] = '12'
                end_date['day'] = '31'      
        else:
            begin_date = parse_date_darwin_core_logic(date)
            end_date = ""
        returned['begin_date'] = begin_date
        returned['end_date'] = end_date      
    return returned
    
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
    if isinstance(var, (int,  float, complex)):
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

    def __init__(self, p_elastic_instance, p_index_name, p_url, p_dataset_name, p_headers, p_logfile, p_mode_direct_zip=False, p_file_path=None ):
        self.m_url = p_url
        self.m_dataset_name = p_dataset_name
        self.m_headers = p_headers       
        self.m_elastic_instance =  p_elastic_instance
        self.m_index_name = p_index_name
        self.m_logfile = p_logfile
        self.m_mode_direct_zip = p_mode_direct_zip
        self.m_file_path = p_file_path
        
    def parse_and_insert_item(self, item, url_specimen):
        try:
            elastic_json = {}
            search_criterias=[]
            what = []
            format = "Web page"
            #type/collection
            type_object=[]
            if "preparations" in item:
                type_object.append(camelcase_to_phrase(item["preparations"]))
            if "organismQuantityType" in item:
                type_object.append(camelcase_to_phrase(item["organismQuantityType"]))
            if "basisOfRecord" in item:
                type_object.append(camelcase_to_phrase(item["basisOfRecord"]))

           
            if 'ownerInstitutionCode' in item:
                var_institution = item["ownerInstitutionCode"]
            if 'institutionCode' in item:
                var_department = item["institutionCode"]
            if 'collectionCode' in item:
                var_main_collection = item["collectionCode"] 
                var_dataset = item["datasetName"]
            if 'datasetName' in item:
                var_sub_collection = item["datasetName"] 
                
            for type in type_object :
                main_type_json = {"main_category": "what", "sub_category": "main_object_category" , "value": type, "sub_category_weight": 10 }
                search_criterias.append(main_type_json)
            main_format_json = {"main_category": "what", "sub_category": "format_of_document" , "value" : format, "sub_category_weight": 9 }
            search_criterias.append(main_format_json)
            #id
            identifiers=[]
            if 'catalogNumber' in item:  
                identifier_json= {"main_category": "what", "sub_category": "object_number" , "value" : item["catalogNumber"], "sub_category_weight": 7 }
                search_criterias.append(identifier_json)
                identifiers.append({"identifier": item["catalogNumber"], "identifier_type": "specimen number" })
            if(len(empty_if_null(item['scientificName']))>0):
                identifiers.append({"identifier": item["scientificName"], "identifier_type": "biological scientific name" })
            if 'typeStatus' in item:
                if(len(empty_if_null(item['typeStatus']))>0):
                    identifiers.append({"identifier": item["typeStatus"], "identifier_type": "biological type status" })
                    #zoological type
                    type_json= {"main_category": "what", "sub_category": "biological_type_status" , "value" : item['typeStatus'], "sub_category_weight": 6 }
                    search_criterias.append(type_json)
            
            

            
            #taxon
            if 'kingdom' in item:
                taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['kingdom'] , "sub_category_weight": 8.8, "rank": "pylum"}
                search_criterias.append(taxon_json)
                what.append(item['kingdom'])
            if 'phylum' in item:
                taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['phylum'] , "sub_category_weight": 8.7, "rank" : "kingdom"}
                search_criterias.append(taxon_json)
            what.append(item['phylum'])
            if 'class' in item:
                taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['class'] , "sub_category_weight": 8.6, "rank" : "class"}
                search_criterias.append(taxon_json)
                what.append(item['class'])
            if 'order' in item:
                taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['order'] , "sub_category_weight": 8.5, "rank" :"order"}
                search_criterias.append(taxon_json)
            what.append(item['order'] )
            if 'family' in item:
                taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['family'] , "sub_category_weight": 8.4, "rank" : "family"}
                search_criterias.append(taxon_json)
                what.append(item['family'])
            if 'genus' in item:
                taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['genus'] , "sub_category_weight": 8.3, "rank" : "genus"}
                search_criterias.append(taxon_json)
                what.append(item['genus'])
            if 'scientificName' in item:
                taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['scientificName'] , "sub_category_weight": 8.2}
                search_criterias.append(taxon_json)
                what.append(item['scientificName'])
            ''' Not used by Thomas ?
            taxon_json = {"main_category": "what", "sub_category": "biological_scientific_name" , "value" : item['acceptedNameUsage'] , "sub_category_weight": 8.1}
            search_criterias.append(taxon_json)
            what.append(item['acceptedNameUsage'] )
            '''
            
            #collector
            if 'recordedBy' in item:
                collector = {"main_category": "who", "sub_category": "collector" , "value" : item['recordedBy']}
                search_criterias.append(collector)
                what.append(item['recordedBy'])
            #identifier
            if 'identifiedBy' in item:               
                identifier = {"main_category": "who", "sub_category": "identifier" , "value" : item['identifiedBy'] }
                search_criterias.append(identifier)
                what.append(item['identifiedBy'])
            
            when=[]
            #collecting date         
            date_from = None
            date_to = None
           
            if 'eventDate' in item:
                if(len(empty_if_null(item['eventDate']))>0):
                    dates_tmp = parse_date_darwin_core(item['eventDate'])
                    if len(dates_tmp['begin_date'])>0:
                        date_from= dates_tmp['begin_date']['year']+'-'+  dates_tmp['begin_date']['month']+'-'+  dates_tmp['begin_date']['day']
                        date_from =  date_from.strip('-')                     
                    if len(dates_tmp['end_date'])>0:
                        date_to= dates_tmp['end_date']['year']+'-'+  dates_tmp['end_date']['month']+'-'+  dates_tmp['end_date']['day']
                        date_to =  date_to.strip('-')
                    if date_from is not None and date_to is not None:
                        when.append({"date_type": "collecting_date" , "date_begin" : date_from, "date_end" : date_to})
                    elif date_from is not None and date_to is None:  
                        when.append({"date_type": "collecting_date" , "date_begin" : date_from, "date_end" : date_from})
            
            
            #identification date            
            date_from = None
            date_to = None            
            if 'dateIdentified' in item:
                if(len(empty_if_null(item['dateIdentified']))>0):
                    dates_tmp = parse_date_darwin_core(item['dateIdentified'])
                    if len(dates_tmp['begin_date'])>0:
                        date_from= dates_tmp['begin_date']['year']+'-'+  dates_tmp['begin_date']['month']+'-'+  dates_tmp['begin_date']['day']
                        date_from =  date_from.strip('-')                     
                    if len(dates_tmp['end_date'])>0:
                        date_to= dates_tmp['end_date']['year']+'-'+  dates_tmp['end_date']['month']+'-'+  dates_tmp['end_date']['day']
                        date_to =  date_to.strip('-')
                    if date_from is not None and date_to is not None:
                        when.append({"date_type": "identification_date" , "date_begin" : date_from, "date_end" : date_to})
                    elif date_from is not None and date_to is None:  
                        when.append({"date_type": "identification_date" , "date_begin" : date_from, "date_end" : date_from})
            
            #water body
            if 'waterBody' in item:
                if(len(empty_if_null(item['waterBody']))>0):
                    water_body = {"main_category": "where", "sub_category": 'water_body' , "value" :item['waterBody'] }
                    what.append(item['waterBody'])
                    search_criterias.append(water_body)
            #island_group
            if 'islandGroup' in  item:
                if(len(empty_if_null(item['islandGroup']))>0):
                    islandGroup = {"main_category": "where", "sub_category": 'island' , "value" :item['islandGroup'] }
                    what.append(item['islandGroup'])
                    search_criterias.append(islandGroup)
            #island
            if 'island' in item:
                if(len(empty_if_null(item['island']))>0):
                    island = {"main_category": "where", "sub_category": 'island' , "value" :item['island'] }
                    what.append(item['island'])
                    search_criterias.append(island)
            #country
            if 'country' in item:
                if(len(empty_if_null(item['country']))>0):
                    new_geo_country = {"main_category": "where", "sub_category": 'country' , "value" :item['country'] }
                    what.append(item['country'])
                    search_criterias.append(new_geo_country)
            if 'countryCode' in item:
                if(len(empty_if_null(item['countryCode']))>0):
                    iso_country = {"main_category": "where", "sub_category": 'ISO_3166-2_country_code' , "value" : item['countryCode'], 'hide_in_facets':True }
                    search_criterias.append(iso_country)
            #locality & habitat
            if 'locality' in item:
                if(len(empty_if_null(item['locality']))>0):
                    locality = {"main_category": "where", "sub_category": 'exact_site' , "value" :item['locality'] }
                    what.append(item['locality'])
                    search_criterias.append(locality)
            #locality & habitat
            if 'verbatimLocality' in item:
                if(len(empty_if_null(item['verbatimLocality']))>0):
                    verbatimlocality = {"main_category": "where", "sub_category": 'exact_site' , "value" :item['verbatimLocality'] }
                    what.append(item['verbatimLocality'])
                    search_criterias.append(verbatimlocality)
            if 'habitat' in item:
                if(len(empty_if_null(item['habitat']))>0):
                    habitat = {"main_category": "where", "sub_category": 'natural_site' , "value" :item['habitat'] }
                    what.append(item['habitat'])
                    search_criterias.append(habitat)
            if 'locationRemarks' in item:
                if(len(empty_if_null(item['locationRemarks']))>0):
                    locality_remarks = {"main_category": "where", "sub_category": "other_geographical_element" , "value" : item['locationRemarks'] }  
                    search_criterias.append(locality_remarks)
            
            #coordinates
            coordinates=[]
            if "latitude" in item and "longitude" in item:
                latitude= item['decimalLatitude']
                longitude = item['decimalLongitude']                
                if latitude is not None and longitude is not None:
                    if(len(empty_if_null(latitude))>0 and len(empty_if_null(longitude))>0) :
                        coordinates.append({"geo_ref_point" :{'lat': latitude  ,'lon':    longitude} })
            
            #ipr
            if 'license' in item :
                license = item['license']
                if(len(empty_if_null(license))>0):
                    license_json = {"main_category": "attribution_and_user_rights", "sub_category": "license" , "value" : license }  
                    search_criterias.append(license_json)
            if 'rightsHolder' in item:
                right_holder = item['rightsHolder']
                if(len(empty_if_null(right_holder))>0):
                    right_json = {"main_category": "attribution_and_user_rights", "sub_category": "right_holder" , "value" : right_holder }  
                    search_criterias.append(right_json)
                
                
            #last modification
            if 'modified' in item:
                last_modification = item["modified"]
                if len(last_modification)==0 :
                    last_modification = datetime.datetime.now()
                    self.m_logfile.write( datetime.datetime.now().strftime("%I:%M:%S:%f%p on %B %d, %Y")+" Warning adding URL: "+url_specimen + " (no modification date, recorded with current date as default value) \n")                    
                else:                   
                    last_modification = dateparser.parse(last_modification)
                last_modification = last_modification.date().strftime('%Y-%m-%dT%I:%M:%S')
                
            #if(len(empty_if_null(last_modification))>0):
            #    print(last_modification)
            #    last_modification=datetime.datetime.strptime(last_modification, '%m/%d/%y' ).strftime( '%Y-%m-%d')
            
            elastic_json= { "id" : null_if_empty(url_specimen), "url" : null_if_empty(url_specimen),     "urls_metadata": [{"url_annex_type": "IPT webservice"}], "object_identifiers" : identifiers, "object_format" : format, "institution" : var_institution, "object_type": type_object    ,"department" : var_department, "main_collection" : var_main_collection,  "sub_collection" : var_sub_collection, "content_text" : null_if_empty(removeduplicate(what)), "search_criteria" : null_if_empty(removeduplicate(search_criterias)), "dates": when, "data_creation_date": null_if_empty(last_modification), "data_modification_date": null_if_empty(last_modification)}
            if len(coordinates)>0: 
                elastic_json["coordinates"] = coordinates
            #print(elastic_json)
            self.m_elastic_instance.index(index=self.m_index_name, doc_type='document', id=elastic_json['id'], body=elastic_json)
        except Exception as inst:
            print("Error adding URL: "+url_specimen)
            self.m_logfile.write( datetime.datetime.now().strftime("%I:%M:%S:%f%p on %B %d, %Y")+" Error adding URL: "+url_specimen + "\n")
            WriteException(self.m_logfile)
            if elastic_json is not None :
                self.m_logfile.write("value:\n")
                self.m_logfile.write(json.dumps(elastic_json))
                self.m_logfile.write("\n")
        #else:
        #    print "Added record with URL "+elastic_json['url']

    def parse_occurrences(self, occ_file, name):
        try:
            
            #datastream = StringIO.StringIO(occ_file.read(name))
            datastream = io.StringIO(occ_file.read(name).decode('utf-8'))
            reader = csv.DictReader(datastream, delimiter='\t')
            print(reader)
            
            print(reader.fieldnames)
            #for row in reader:
            # 
            iExc = 0            
            for row in reader:
                try:                   
                    try:                                          
                        self.parse_and_insert_item(row, row['occurrenceID'])
                    except Exception:
                        iExc += 1 
                        print("Exception "+str( iExc )+" for "+row['occurrenceID'])
                        PrintException()
                except:
                    iExc += 1 
                    print("Generator Exception "+str( iExc ))
                    print(row)
                    
                    #print(chardet.detect(json.dumps(row_ori)))
                    PrintException()
        except Exception:
            PrintException()

    def handle_ipt_service(self, p_url, p_dataset):
        try:        
            print("debug")
            print(p_url + p_dataset)
            u = urllib.urlopen(p_url + p_dataset)
            print(p_url + p_dataset)
            print(u)
            tmp=io.BytesIO(u.read())
            zip_handler = zipfile.ZipFile(tmp, 'r')
            print(zip_handler.infolist())            
            print(zip_handler.namelist())          
            return zip_handler            
        except Exception:
             PrintException()
             
    def handle_zip(self, p_zip_file):
        try:      
            zip_handler = zipfile.ZipFile(p_zip_file, 'r')
            print(zip_handler.infolist())            
            print(zip_handler.namelist())          
            return zip_handler            
        except Exception:
             PrintException()
             
    def run(self):
        try:
            if self.m_mode_direct_zip == False :
                zip_handler = self.handle_ipt_service(self.m_url, self.m_dataset_name)
                #print(files['occurrence.txt'])
                #occ = files['occurrence.txt']
                tmp =self.parse_occurrences(zip_handler, "occurrence.txt")
            else:
                zip_handler = self.handle_zip(self.m_file_path)
                tmp =self.parse_occurrences(zip_handler, zip_handler.namelist()[0])
        except Exception:
             PrintException()


####################### end class ###############        
        

url=params.URL_IPT
url= url+"/archive.do?r="

dataset_name = params.IPT_DATASET

elasticInstance = Elasticsearch(
    [params.ES_SERVER],    
    port=params.ES_PORT,
    use_ssl = False
)
indexname=params.ES_INDEX
logfile = open(params.LOG_FILE, 'w+')

ipt_parser =  IPTParser(elasticInstance, indexname, url, dataset_name, None, logfile, params.MODE_ZIP, params.FILE_PATH)
ipt_parser.run()


#close(logfile)
#python 3 +
logfile.close()