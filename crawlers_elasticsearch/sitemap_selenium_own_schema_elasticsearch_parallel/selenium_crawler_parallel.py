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

def threadSitemap(elastic_instance, index_name, ns_sm, ns_sm_img, selenium_driver, sitemap_text, first_index, last_index, institution, bundle_name):
	try:
		sitemap_tree = etree.fromstring(sitemap_text)
	except Exception, e:
		print(str(e))
	i=0
	for urlElem in sitemap_tree.iter('{%s}loc'%(ns_sm)):
		if i>= first_index and i< last_index:
			url = urlElem.text
			selenium_driver.get(url)
			sleep(0.5)
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

			try: # Try to set the title
				title = soup.html.head.title.string.decode("utf-8")
			except:
				print "Error: Could not parse title tag found at URL: "+url
				continue #Could not parse <title> tag.  Skip.

			try: # Try to set the body
				body = str(soup.html.body).decode("utf-8")
				#print body
			except:
				print "Error: Could not parse body tag found at URL: "+url
				continue #Could not parse <body> tag.  Skip.

				# Get an md5 hash of the url for the unique id
			url_md5 = hashlib.md5(url).hexdigest()

	
				
			#values_to_add={"id": url_md5, "url_s": url, "text": body,"title": body, "type" :'webpage'}
			values_to_add={"id": url, "institution": institution ,"url": url, "content": body, "content_ngrams":body, "label": url, "title" :'webpage', 'bundle_name': bundle_name}
			#parse images
			locs=[]
			captions=[]
			titles=[]
			for imgElem in urlElem.findall('../{%s}image'%(ns_sm_img)):
				print "image found"
				try:
					locImg = imgElem.find('{%s}loc'%(ns_sm_img)).text
				except:
					pass
				else:
					if len(locImg) >0 :
						locs.append(locImg)
						print "Img loc added to array"
				try:
					captionImg = imgElem.find('{%s}caption'%(ns_sm_img)).text
				except:
					pass
				else:
					if len(captionImg) >0 :
						captions.append(captionImg)
						print "Img caption added to array"
				try:
					titleImg = imgElem.find('{%s}title'%(ns_sm_img)).text
				except:
					pass
				else:
					if len(titleImg) >0 :
						titles.append(titleImg)
						print "Img title added to array"
				if len(locs)>0 :
					try:
						values_to_add["images"]=locs
					except:
						print "Error: cannot add image"
						pass
					else:
						print "image added"

				if len(titles)>0 :
					try:
						values_to_add["titles"]=titles
					except:
						print "Error: cannot add titles of image"
						pass
					else:
						print "titles of image added"

				if len(captions)>0 :
					try:
						values_to_add["captions"]=captions
					except:
						print "Error: cannot add titles of captions"
						pass
					else:
						print "captions of image added"
			try: # Add to the elasticsearch instance
				#print values_to_add
				elastic_instance.create(index=index_name, doc_type='document', id=url, body=values_to_add)
		
			except Exception as inst:
				print "Error adding URL: "+url
				print "\tWith Message: "+str(inst)
			else:
				print "Added Page \""+title+"\" with URL "+url
		i=i+1
#---------------------------------------------------------------------------------------------
print(time.ctime())
vdisplay = Xvfb()




vdisplay.start()
cpu_counts = multiprocessing.cpu_count()
print(cpu_counts)

sitemap="http://digit03.africamuseum.be/dbdigit03/sitemap_google"


ns_sm="http://www.sitemaps.org/schemas/sitemap/0.9"
ns_sm_img="http://www.google.com/schemas/sitemap-image/1.1"


elasticInstance = Elasticsearch(
    ['localhost'],
    http_auth=('elastic', 'changeme'),
    port=9200,
    use_ssl=False
)
indexname="naturalheritage"


driver = webdriver.Firefox()

count_elems=2000



print("go")
try:
	webFile = urllib2.urlopen(sitemap)
	print("go1")

	sm=webFile.read()
	webFile.close()
except Exception, e:
	print(str(e))
print("go2")




#count_elems = sitemapTree.xpath('count(//x:loc)',namespaces={'x': ns_sm})

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
                                args=(elasticInstance, indexname, ns_sm, ns_sm_img, driver, sm, min_elem, max_elem, 'RMCA', 'digit03'))
	processes.append(p)	

for p in processes:
	p.start()

for p in processes:
	p.join()

#try: # Try to commit the additions
#	solrInstance.commit()
#except:
#	print "Could not Commit Changes to Solr Instance - check logs"
#else:
print "Success documents added to index"

print(time.ctime())

vdisplay.stop()

