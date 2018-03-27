import urllib2
import urllib
import json
from elasticsearch import Elasticsearch

import psycopg2
import psycopg2.extras
import linecache
import sys
import json

# sys.setdefaultencoding() does not exist, here!
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

def removeduplicate(array):
    return[json.loads(y) for y in list(set([json.dumps(x).encode('utf-8') for x in array]))]


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

def PrintException(p_logfile):
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)
	p_logfile.write('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
	p_logfile.write('\n')


class DarwinParser(object):

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
		
	def set_pg_connection(self, p_connection_string, p_prefix_json="http://www.africamuseum.be/collections/browsecollections/naturalsciences/biology/ichtyology/darwin_specimen?id_spec=", p_prefix_json_metadata="http://193.190.223.58/public.php/search/getjson?specimennumber="):
		try:
			self.m_connection_string= p_connection_string
			self.m_conn = psycopg2.connect(self.m_connection_string)
			self.m_prefix_json = p_prefix_json
			self.m_prefix_json_metadata = p_prefix_json_metadata
			self.m_go_database = True
		except Exception, e:
			PrintException(self.m_logfile)
		

	def getLastPage(self, data):
		try:
			return data["last_url"]
		except Exception, e:
			 PrintException(self.m_logfile)

	def getNextPage(self, data):
		try:
			return data["next_url"]
		except Exception, e:
			 PrintException(self.m_logfile)

	def get_page_content(self, p_url, p_params, p_headers):
		try:
			request = urllib2.Request(p_url+p_params, headers=p_headers)
			contents = urllib2.urlopen(request).read()
			return contents
		except Exception, e:
			 PrintException(self.m_logfile)
			 
	def get_page_content_pg(self):
		try:
			query="""SELECT distinct string_agg(DISTINCT id::varchar, '|') as ids, 
			%s||code_display as public_url, collection_name, collection_code, (SELECT modification_date_time FROM users_tracking where referenced_relation='specimens' and record_id= max(specimens.id)	 GROUP BY modification_date_time ,users_tracking.id having users_tracking.id=max(users_tracking.id) limit 1) as last_modification, code_display, string_agg(DISTINCT taxon_path::varchar, '|') as taxon_paths, string_agg(DISTINCT taxon_ref::varchar, '|') as taxon_ref,
					string_agg(DISTINCT taxon_name, '|') as taxon_name,
					string_agg(DISTINCT	 history, '|') as history_identification
					,
					 string_agg(DISTINCT gtu_country_tag_value, '|') as country,  string_agg(DISTINCT gtu_others_tag_value, '|') as geographical,		   
					fct_mask_date(gtu_from_date,
					gtu_from_date_mask) as date_from_display,
					fct_mask_date(gtu_to_date,
					gtu_to_date_mask) as date_to_display,
					coll_type,								 
					STRING_AGG(urls_thumbnails, '|') as urls_thumbnails,  STRING_AGG(image_category_thumbnails, '|') as image_category_thumbnails, STRING_AGG(contributor_thumbnails,'|') as contributor_thumbnails, STRING_AGG(disclaimer_thumbnails,'|') as disclaimer_thumbnails, STRING_AGG(license_thumbnails, '|') as license_thumbnails , STRING_AGG(display_order_thumbnails::varchar, '|') as display_order_thumbnails,
					STRING_AGG(urls_image_links, '|') as urls_image_links,	 STRING_AGG(image_category_image_links, '|') as image_category_image_links, STRING_AGG(contributor_image_links,'|') as contributor_image_links, STRING_AGG(disclaimer_image_links,'|') as disclaimer_image_links, STRING_AGG(license_image_links, '|') as license_image_links , STRING_AGG(display_order_image_links::varchar, '|') as display_order_image_links,
					STRING_AGG(urls_3d_snippets, '|') as urls_3d_snippets,	STRING_AGG(image_category_3d_snippets, '|') as image_category_3d_snippets, STRING_AGG(contributor_3d_snippets,'|') as contributor_3d_snippets, STRING_AGG(disclaimer_3d_snippets,'|') as disclaimer_3d_snippets, STRING_AGG(license_3d_snippets, '|') as license_3d_snippets , STRING_AGG(display_order_3d_snippets::varchar, '|') as display_order_3d_snippets,
					longitude, latitude
					,count(*) OVER() AS full_count,collector_ids, 
					(SELECT string_agg(formated_name, '|') from people where id = any(collector_ids)) as collectors
					, donator_ids,
					(SELECT array_agg(formated_name) from people where id = any(donator_ids)) as donators
					,
					string_agg(distinct tag_locality, '| ') as localities	
					from 
					(SELECT specimens.id,
					collections.code as collection_code, collections.name as collection_name, 
					COALESCE(codes.code_prefix,'')||COALESCE(codes.code_prefix_separator,'')||COALESCE(codes.code,'')||COALESCE(codes.code_suffix_separator,'')||COALESCE(codes.code_suffix,'') as code_display, full_code_indexed, taxon_path, taxon_ref, collection_ref , gtu_country_tag_indexed , gtu_country_tag_value, 
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
					ext_links_thumbnails.url as urls_thumbnails, ext_links_thumbnails.category image_category_thumbnails, ext_links_thumbnails.contributor contributor_thumbnails, ext_links_thumbnails.disclaimer disclaimer_thumbnails, ext_links_thumbnails.license license_thumbnails, ext_links_thumbnails.display_order display_order_thumbnails,
					ext_links_image_links.url as urls_image_links, ext_links_image_links.category image_category_image_links, ext_links_image_links.contributor contributor_image_links, ext_links_image_links.disclaimer disclaimer_image_links, ext_links_image_links.license license_image_links, ext_links_image_links.display_order display_order_image_links,
					ext_links_3d_snippets.url as urls_3d_snippets, ext_links_3d_snippets.category image_category_3d_snippets, ext_links_3d_snippets.contributor contributor_3d_snippets, ext_links_3d_snippets.disclaimer disclaimer_3d_snippets, ext_links_3d_snippets.license license_3d_snippets, ext_links_3d_snippets.display_order display_order_3d_snippets,
					gtu_location[1] as latitude,
					gtu_location[0] as longitude,
					notion_date as identification_date, 
					notion_date_mask as identification_date_mask,
					coalesce(fct_mask_date(notion_date, notion_date_mask)||': ','')||taxon_name as history,
					 specimens.gtu_ref,
					group_type, sub_group_type,
					tag
					, group_type||' -x- '||sub_group_type||' -:- '||tag as tag_locality 
					FROM specimens
					LEFT JOIN
					collections ON
					specimens.collection_ref=collections.id
					LEFT JOIN 
					codes
					ON codes.referenced_relation='specimens' and code_category='main' and specimens.id=codes.record_id
					LEFT JOIN
					ext_links as ext_links_thumbnails
					ON
					specimens.id=ext_links_thumbnails.record_id and ext_links_thumbnails.referenced_relation='specimens' and ext_links_thumbnails.category='thumbnail'
					
					LEFT JOIN
					ext_links as ext_links_image_links
					ON
					specimens.id=ext_links_image_links.record_id and ext_links_image_links.referenced_relation='specimens' and ext_links_image_links.category='image_link'
					
					LEFT JOIN
					ext_links as ext_links_3d_snippets
					ON
					specimens.id=ext_links_3d_snippets.record_id and ext_links_3d_snippets.referenced_relation='specimens' and ext_links_3d_snippets.category='html_3d_snippet'
					
					LEFT JOIN identifications
					on identifications.referenced_relation='specimens'
					and specimens.id= identifications.record_id
					and notion_concerned='taxonomy'
					LEFT JOIN tags
					ON specimens.gtu_ref=tags.gtu_ref
					order by group_ref
					) as specimens
					WHERE collection_name=%s
					GROUP BY 
					collection_name,
					collection_code,
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
					  , donator_ids;"""
			cur = self.m_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute(query, (self.m_prefix_json, self.m_collection)	)
			for item in cur:
				url_specimen= self.m_prefix_json + item['code_display']
				self.parse_and_insert_item(item, url_specimen)
		except Exception, e:
			 PrintException(self.m_logfile)

	def parse_specimen(self, url_specimen, p_headers):
		try:
			request = urllib2.Request(url_specimen, headers = p_headers)
			contents_tmp = urllib2.urlopen(request).read()
			contents= json.loads(contents_tmp)
			for item in contents:
				self.parse_and_insert_item(item, url_specimen)
		except Exception, e:
			PrintException(self.m_logfile)
			
	def parse_and_insert_item(self, item, url_specimen):
		try:
			type_object="Natural sciences specimen"
			public_url= item["public_url"]
			#print(public_url)
			coll_type = item["coll_type"]
			specimen_code = item["code_display"]
			collection_name = item["collection_name"]
			collection_code = item["collection_code"]
			taxon_names = empty_if_null(item["taxon_name"]).split("|")
			history_identification = empty_if_null(item["history_identification"]).split("|")
			collectors = empty_if_null(item['collectors']).split("|")
			donators = empty_if_null(item['collectors']).split("|")
			#print(collectors)
			#Geographical
			countries = empty_if_null(item["country"]).split("|")
			geographicals = empty_if_null(item["geographical"]).split("|")
			localities = empty_if_null(item['localities']).split("|")
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
			tmpTypesMultimedia=["thumbnails", "image_links", "3d_snippets"]
			for field in tmpTypesMultimedia:
				array_urls=[]
				array_category=[]
				array_contributor=[]
				array_disclaimer=[]
				array_license=[]
				array_display_order=[]
				#print "urls_"+field
				#print item["urls_"+field]
				if item["urls_"+field] is not None:
					array_urls=empty_if_null(item["urls_"+field]).split('|')
				if item["image_category_"+field] is not None:	 
					array_category=empty_if_null(item["image_category_"+field]).split('|')
				if item["contributor_"+field] is not None:
					array_contributor=empty_if_null(item["contributor_"+field]).split('|')
				if item["disclaimer_"+field] is not None:
					array_disclaimer=empty_if_null(item["disclaimer_"+field]).split('|')
				if item["license_"+field] is not None:
					array_license=empty_if_null(item["license_"+field]).split('|')
				if item["display_order_"+field] is not None:
					array_display_order=empty_if_null(item["display_order_"+field]).split('|')
				
				tmpArray={}
				tmpArray["urls_"+field]={}
				tmpArray["image_category_"+field]={}
				tmpArray["contributor_"+field]={}
				tmpArray["disclaimer_"+field]={}
				tmpArray["license_"+field]={}
				tmpArray["display_order_"+field]={}
				key=0
				for value in array_display_order:
					if len(array_urls)>key:
						tmpArray["urls_"+field][value]=array_urls[key]
					if len(array_category)>key:
						tmpArray["image_category_"+field][value]=array_category[key]
					if len(array_contributor)> key:
						tmpArray["contributor_"+field][value]=array_contributor[key]
					if len(array_disclaimer)>key:
						tmpArray["disclaimer_"+field][value]=array_disclaimer[key]
					if len(array_license) > key:
						tmpArray["license_"+field][value]=array_license[key]
					if len(array_display_order)> key:
						tmpArray["display_order_"+field][value]=array_display_order[key]
					key	 = key + 1
				for field2 in tmpArray:					
					item[field2] = ';'.join(tmpArray[field2].values())
			##
			
			urls_thumbnails = empty_if_null(item['urls_thumbnails']).split('|')
			display_order_thumbnails = empty_if_null(item['display_order_thumbnails']).split('|')
			contributor_thumbnails = empty_if_null(item['contributor_thumbnails']).split('|')
			disclaimer_thumbnails = empty_if_null(item['disclaimer_thumbnails']).split('|')	
			license_thumbnails = empty_if_null(item['license_thumbnails']).split('|')
			urls_image_links = empty_if_null(item['urls_image_links']).split('|')
			display_order_image_links = empty_if_null(item['display_order_image_links']).split('|')
			contributor_image_links = empty_if_null(item['contributor_image_links']).split('|')
			disclaimer_image_links = empty_if_null(item['disclaimer_image_links']).split('|')	
			license_image_links = empty_if_null(item['license_image_links']).split('|')
				

			urls_3d_snippets = empty_if_null(item['urls_3d_snippets']).split('|')
			display_order_3d_snippets = empty_if_null(item['display_order_3d_snippets']).split('|')
			contributor_3d_snippets = empty_if_null(item['contributor_3d_snippets']).split('|')
			disclaimer_3d_snippets = empty_if_null(item['disclaimer_3d_snippets']).split('|')	
			license_3d_snippets = empty_if_null(item['license_3d_snippets']).split('|')
				
							
			last_modification = item["last_modification"]

			#treatments
			
			what = []
			for taxon_name in taxon_names:
				what.append(taxon_name)
			for history_identification_elem in history_identification:
				 what.append("History identification : " +	history_identification_elem)
			if len(empty_if_null(coll_type))>0: 
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
				
			
			url_json=self.m_prefix_json_metadata+specimen_code
			identifiers=[]
			identifiers =  [{"identifier": specimen_code, "identifier_type": "specimen number" },  {"identifier":  coll_type, "identifier_type": "Zoological type status"} ]
			for taxon_name in taxon_names:
				identifiers.append({"identifier": taxon_name, "identifier_type": "scientific name (zoological)"})
			format = "Web page"
			type = "Zoological specimen"
			search_criterias=[]
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
						new_locality_geo = {"main_category": "where", "sub_category": type_loc[1].strip().lower() , "value" : items[1].strip() }
					else:
						new_locality_geo = {"main_category": "where", "sub_category": items[0].strip().lower() , "value" : items[1].strip() }
					search_criterias.append(new_locality_geo)
					what.append(items[1].strip())
				else:
					new_locality_geo = {"main_category": "where", "sub_category": "other geographical element" , "value" : locality }					 
			new_geo_geographical = {"main_category": "where", "sub_category": "country" , "value" : country.strip() }
			search_criterias.append(new_geo_country)
			coordinates=[]
			if latitude is not None and longitude is not None:
				coordinates.append({"geo_ref_point" :{'lat': latitude  ,'lon':	longitude} })
			#WHEN
			when=[]
			when.append({"date_type": "collecting_date" , "date_begin" : date_object_begin, "date_end" : date_object_end})

			
			
			elastic_json= { "id" : null_if_empty(public_url), "url" : null_if_empty(public_url),	 "urls_metadata": [{"url_value": url_json, "url_annex_type": "Darwin JSON webservice"}], "object_identifiers" : identifiers, "object_format" : format, "institution" : self.m_institution, "object_type": type	,"department" : self.m_department, "main_collection" : self.m_parent_collection,  "sub_collection": self.m_collection , "content_text" : null_if_empty(removeduplicate(what)), "search_criteria" : null_if_empty(removeduplicate(search_criterias)), "dates": when, "data_creation_date": null_if_empty(last_modification), "data_modification_date": null_if_empty(last_modification)}
			if len(coordinates)>0: 
				elastic_json["coordinates"] = coordinates
			self.m_elastic_instance.create(index=self.m_index_name, doc_type='document', id=elastic_json['id'], body=elastic_json)
		except Exception as inst:
			print "Error adding URL: "+url_specimen
			self.m_logfile.write("Error adding URL: "+url_specimen)
			self.m_logfile.write('\n')
			PrintException(self.m_logfile)
			self.m_logfile.write("value:\n")
			self.m_logfile.write(json.dumps(elastic_json))
			self.m_logfile.write("\n")
		else:
			print "Added Article with URL "+elastic_json['url']
		
	

	def browse_and_map_items(self, data):
		try:
			for item in data['records']:
				url_specimen=item['url_specimen']
				print(url_specimen)
				self.parse_specimen(url_specimen, self.m_headers)
		except Exception, e:
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
		except Exception, e:
			 PrintException(self.m_logfile)

	def run(self):
		try:
			if not self.m_go_database:
				self.handle_darwin_service(self.m_url, self.m_params, self.m_headers)
			else:
				self.get_page_content_pg()
		except Exception, e:
			 PrintException(self.m_logfile)

####################### end class ###############
logfile = open('main.log', 'w+')
url="http://193.190.223.58/public.php/search/getcollectionjson?"
collection_code='"MAMMA_RMCA"'
#collection_code='INSECTA_TYPES_DIGIT03'
parent_collection='Vertebrates'
collection_name='Mammalogy'
#collection_name='Insecta Types (DIGIT 03)'
params = urllib.urlencode({'collection' :  collection_code})
request_headers = {
"Accept": "application/json",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0| WOW64| rv:40.0) Gecko/20100101 Firefox/40.0",
"Connection": "keep-alive" 
}
elasticInstance = Elasticsearch(
	['localhost'],
	http_auth=('elastic', 'changeme'),
	port=9200,
	use_ssl=False
)
indexname="naturalheritage"



darwin_parser =	 DarwinParser(elasticInstance, indexname, url, params, request_headers, "RMCA", "Zoology",parent_collection, collection_name, logfile )
darwin_parser.set_pg_connection("host='193.190.223.58' dbname='darwin2' user='darwin2' password='darwin123'")
darwin_parser.run()


