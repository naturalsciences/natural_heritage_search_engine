import multiprocessing


from elasticsearch import Elasticsearch
import hashlib
import sys
from BeautifulSoup import BeautifulSoup
from xvfbwrapper import Xvfb
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
#from xml.etree.ElementTree import fromstring
from lxml import etree
import time
import urllib2

def threadSitemap(elastic_instance, index_name, selenium_driver, filename, first_index, last_index, institution, bundle_name):
	i=0
	#for urlElem in sitemap_tree.iter('{%s}loc'%(ns_sm)):
	with open(filename) as fp:
		for url in fp:
			if i>= first_index and i< last_index:
				#url = urlElem.text
				url=url.rstrip()
				selenium_driver.get(url)
				sleep(1)
				html_source = selenium_driver.page_source
				try: # Try to parse the HTML of the page
						soup = BeautifulSoup(html_source)
				except Exception, e:
					print(str(e))
					print "Error: Cannot parse HTML from URL: "+url
					continue # Cannot parse HTML.  Skip.

				if soup.html == None: # Check if there is an <html> tag
					print "Error: No HTML tag found at URL: "+url
					continue #No <html> tag.  Skip.

				
				title=url
				try: # Try to set the body
					body = str(soup.html.body).decode("utf-8")
					#print body
				except:
					print "Error: Could not parse body tag found at URL: "+url
					continue #Could not parse <body> tag.  Skip.

					# Get an md5 hash of the url for the unique id
				url_md5 = hashlib.md5(url).hexdigest()

	
				
				values_to_add={ "url": url, "institution": institution , "content":body, "content_ngrams": body, "label": url, "title" :'webpage', 'bundle_name': bundle_name}
			
				#parse images
				locs=[]
				captions=[]
				titles=[]
				try: # Add to the Elasticsearch instance
					
					elastic_instance.create(index=index_name, doc_type='document', id=url, body=values_to_add)
		
				except Exception as inst:
					print "Error adding URL: "+url
					print "\tWith Message: "+str(inst)
				else:
					print "Added Page \""+title+"\" with URL "+url
				i=i+1
			else:
				break
			
#---------------------------------------------------------------------------------------------
print(time.ctime())
vdisplay = Xvfb()




vdisplay.start()
cpu_counts = 1  #multiprocessing.cpu_count()
print(cpu_counts)

url_filename="./commodities_drcmining_url_only76.txt"

elasticInstance = Elasticsearch(
    ['localhost'],
    http_auth=('elastic', 'changeme'),
    port=9200,
    use_ssl=False
)
indexname="naturalheritage"



#solrUrl = 'http://localhost:8983/solr/naturalheritage'

driver = webdriver.Firefox()


#solrInstance = solr.Solr(solrUrl) # Solr Connection object

print("go")

count_elems=120
print(count_elems)

elem_per_threads=count_elems/cpu_counts
elem_per_threads=int(elem_per_threads)
print(elem_per_threads)

print(time.ctime())

processes = []

for i in range(cpu_counts):
	min_elem= i * elem_per_threads
	if i == range:
		max_elem=count_elems-((i-1) * elem_per_threads)
	else:
		max_elem= (i+1)*elem_per_threads
	print(i)
	print(min_elem)
	print(max_elem)
	p=multiprocessing.Process(target=threadSitemap,
                                args=(elasticInstance, indexname, driver, url_filename, min_elem, max_elem, 'RMCA', 'commodities'))
	processes.append(p)	

for p in processes:
	p.start()

for p in processes:
	p.join()

try: # Try to commit the additions
	solrInstance.commit()
except:
	print "Could not Commit Changes to Elastic Instance - check logs"
else:
	print "Success documents added to index"

print(time.ctime())

vdisplay.stop()

