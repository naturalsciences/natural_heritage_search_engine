import urllib2
import urllib
import json
from elasticsearch import Elasticsearch

import linecache
import sys


def null_if_empty(var):
  if var is None:
    return None
  if len(var)==0:
    return None
  return var

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)



class DarwinParser(object):

	def __init__(self, p_elastic_instance, p_index_name, p_url, p_params, p_headers, p_institution, p_department, p_parent_collection, p_collection ):
		self.m_url = p_url
		self.m_params = p_params
		self.m_headers = p_headers
		self.m_institution= p_institution 
		self.m_department = p_department
		self.m_parent_collection = p_parent_collection
		self.m_collection = p_collection
		self.m_elastic_instance =  p_elastic_instance
		self.m_index_name = p_index_name

	def getLastPage(self, data):
		try:
			return data["last_url"]
		except Exception, e:
			 PrintException()

	def getNextPage(self, data):
		try:
			return data["next_url"]
		except Exception, e:
			 PrintException()

	def get_page_content(self, p_url, p_params, p_headers):
		try:
			request = urllib2.Request(p_url+p_params, headers=p_headers)
			contents = urllib2.urlopen(request).read()
			return contents
		except Exception, e:
			 PrintException()

	def parse_specimen(self, url_specimen, p_headers):
		try:
			request = urllib2.Request(url_specimen, headers = p_headers)
			contents_tmp = urllib2.urlopen(request).read()
			contents= json.loads(contents_tmp)
			for item in contents:
				type_object="Natural sciences specimen"
				public_url= item["public_url"] 
				coll_type = item["coll_type"]
				specimen_code = item["code_display"]
				collection_name = item["collection_name"]
				collection_code = item["collection_code"]
				taxon_name = item["taxon_name"]
				history_identification = item["history_identification"]
				collectors = item ['collectors']
				donators = item ['collectors']
				print(collectors)
				#Geographical
				country = item["country"]
				geographical = item["geographical"]
				localities = item['localities']
				latitude= item['latitude']
				longitude = item['longitude']
				#Date
				date_from_display = item["date_from_display"]
				print(date_from_display)
				year_from = date_from_display[:4]
				print(year_from)
				if(year_from=="xxxx"):
					year_from=""
				date_to_display = item["date_to_display"]
				print(date_to_display)
				year_to = date_to_display[:4]
				print(year_to)
				if(year_to=="xxxx"):
					year_to=""
				if(len(year_to)>0):
					date_range = date_from_display + " to " + date_to_display
				else:
					date_range = date_from_display
				print(date_range)
				
				#multimedia
				urls_thumbnails = item['urls_thumbnails'].split(';')
				display_order_thumbnails = item['display_order_thumbnails'].split(';')
				contributor_thumbnails = item['contributor_thumbnails'].split(';')
				disclaimer_thumbnails = item['disclaimer_thumbnails'].split(';')	
				license_thumbnails = item['license_thumbnails'].split(';')
			
				urls_image_links = item['urls_image_links'].split(';')
				display_order_image_links = item['display_order_image_links'].split(';')
				contributor_image_links = item['contributor_image_links'].split(';')
				disclaimer_image_links = item['disclaimer_image_links'].split(';')	
				license_image_links = item['license_image_links'].split(';')
				

				urls_3d_snippets = item['urls_3d_snippets'].split(';')
				display_order_3d_snippets = item['display_order_3d_snippets'].split(';')
				contributor_3d_snippets = item['contributor_3d_snippets'].split(';')
				disclaimer_3d_snippets = item['disclaimer_3d_snippets'].split(';')	
				license_3d_snippets = item['license_3d_snippets'].split(';')
					
			
				
				last_modification = item["last_modification"]

				#treatments
				#who = collectors + donators
				where = geographical + "\n" + localities
				what = "Taxon Name :" + taxon_name + ".\n" + "History identification : " +  history_identification + ".\n" + "Type :" + coll_type 
				keywords=[]
				keywords.append(coll_type)
				keywords.append(taxon_name)
				keywords.append(country)
				keywords.append(geographical)

				date_object_begin = None
				date_object_end = None
				date_object_text = date_range
				if(len(year_from)>0):
					date_object_begin = year_from + "-01-01"
				if(len(year_to)>0):
					date_object_end = year_to + "-31-12"
				

				elastic_json={"id": null_if_empty(public_url), "institution": null_if_empty(self.m_institution ), "department" : null_if_empty( self.m_department ), "bundle_name" : null_if_empty(collection_name), "object_identifier": null_if_empty(specimen_code ), "object_type" : null_if_empty(coll_type), 
				"url": null_if_empty(public_url), 
				"url_metadata": null_if_empty(url_specimen), 
				"collectors" : null_if_empty(collectors), "donators" : null_if_empty(donators), "main_object" : null_if_empty(taxon_name), "content": null_if_empty(what), "content_ngrams": null_if_empty(what), "keywords": null_if_empty(keywords), "title" : null_if_empty(taxon_name ),  
				"country" : null_if_empty(country), "geographical" : null_if_empty(where), "latitude" : null_if_empty(latitude), "longitude" : null_if_empty(longitude) ,
				"date_object_begin" : null_if_empty(date_object_begin), "date_object_end" : null_if_empty(date_object_end), "date_object_text" : null_if_empty(date_object_text),
				 "thumbnails.urls" : null_if_empty(urls_thumbnails), "thumbnails.display_order" : null_if_empty(display_order_thumbnails), "thumbnails.contributor" : null_if_empty(contributor_thumbnails), "thumbnails.disclaimer" : null_if_empty(disclaimer_thumbnails), "thumbnails.license" : null_if_empty(license_thumbnails),
				 "images.urls" : null_if_empty(urls_image_links), "images.display_order" : null_if_empty(display_order_image_links), "images.contributor" : null_if_empty(contributor_image_links), "images.disclaimer" : null_if_empty(disclaimer_image_links), "images.license" : null_if_empty(license_image_links),
				"iframe_3d.urls" : null_if_empty(urls_3d_snippets), "iframe_3d.display_order" : null_if_empty(display_order_3d_snippets), "iframe_3d.contributor" : null_if_empty(contributor_3d_snippets), "iframe_3d.disclaimer" : null_if_empty(disclaimer_3d_snippets), "iframe_3d.license" : null_if_empty(license_3d_snippets),
"modification_date" : null_if_empty(last_modification)}
				try: # Add to the elasticsearch instance
				#print values_to_add
					self.m_elastic_instance.create(index=self.m_index_name, doc_type='document', id=elastic_json['id'], body=elastic_json)
				except Exception as inst:
					print "Error adding URL: "+url
					PrintException()
				else:
					print "Added Article with URL "+elastic_json['url']
		except Exception, e:
			PrintException()

	def browse_and_map_items(self, data):
		try:
			for item in data['records']:
				url_specimen=item['url_specimen']
				print(url_specimen)
				self.parse_specimen(url_specimen, self.m_headers)
		except Exception, e:
			 PrintException()

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
		except Exception, e:
			 PrintException()

	def run(self):
		try:
			self.handle_darwin_service(self.m_url, self.m_params, self.m_headers)
		except Exception, e:
			 PrintException()

####################### end class ###############

url="http://193.190.223.58/public.php/search/getcollectionjson?"
collection_code='ICHTYO'
#collection_code='INSECTA_TYPES_DIGIT03'
parent_collection='Vertebrates'
collection_name='Mammalogy'
params = urllib.urlencode({'collection' :  collection_code})
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



darwin_parser =  DarwinParser(elasticInstance, indexname, url, params, request_headers, "RMCA", "Zoology",parent_collection, collection_name )
darwin_parser.run()


