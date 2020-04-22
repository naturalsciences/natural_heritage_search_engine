import requests
from lxml import html


class ParsePage:

    def __init__(self, p_endpoint, p_institution, p_headers= {"Accept": "application/json","User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0","Connection": "keep-alive"}):
        self.endpoint = p_endpoint
        self.institution=p_institution
        self.headers=p_headers
        self.returned={}
        
    def attribute_value(self, html_xml, itemprop, output_key):
        tmplist=html_xml.xpath("//td[@itemprop='"+ itemprop +"']")
        if(len(tmplist)>0):
            self.returned[output_key]=tmplist[0].text
            
    def parse_response(self, p_json):        
        self.returned["creation_date"]=p_json["creation_date"]
        self.returned["modification_date"]=p_json["modification_date"]
        html_part=p_json["text"]["data"]
        html_xml = html.fromstring(html_part)
        self.attribute_value(html_xml, 'PScienStaff', 'permanent_scientific_staff')
        self.attribute_value(html_xml, 'NPScienStaff', 'non_permanent_scientific_staff')
        self.attribute_value(html_xml, 'PScienStaffCol', 'permanent_scientific_staff_in_collection') 
        self.attribute_value(html_xml, 'NPScienStaffCol', 'non_permanent_scientific_staff_in_collection')
        self.attribute_value(html_xml, 'PScienStaffPhD', 'permanent_post_docs_phd') 
        self.attribute_value(html_xml, 'NPScienStaffPhD', 'non_permanent_post_docs_phd')
        self.attribute_value(html_xml, 'PScienStaffOthers', 'permanent_others') 
        self.attribute_value(html_xml, 'NPScienStaffOthers', 'non_permanent_others')        
        
    def curl_connect(self):
        content = requests.get(self.endpoint, headers=self.headers)
        self.parse_response(content.json())

        
    def parse(self):
        self.curl_connect()
    
    def get_es_json(self):
        self.parse()
        return self.returned
        



        
     