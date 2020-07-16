import json
from elasticsearch import Elasticsearch
import random

INDEX_NAME="cetaf_passport"
URL_ID="http://collections.naturalsciences.be/cpb/nh-collections/countries/belgium/be-rbins/"

coll_struct={}
coll_struct["Botany"]=["Vascular plants","Bryophytes (mosses)","Algae" ]
coll_struct["Mycology"]=["Fungi and lichens" ]
coll_struct["Zoology Invertebrates"]=["Arthropods - insects", "Arthropods - arachnids", "Arthropods - crustaceans & myriapods", "Mollusks (bivalves, gastropods, cephalopods)", "Cnidaria (corals, jellyfish, anemones)", "Porifera (sponges)", "Other (other taxonomic groups)"]
coll_struct["Zoology Vertebrates"]=["Fishes", "Amphibians", "Reptiles", "Birds", "Mammals"]
list_paths={}

addresses=[{"city":"Brussel",
           "country":"Belgium",
           "email": "info@naturalsciences.be",
           "postcode":"1000",
           "street": "Rue Vautier",
           "phone":"+32 (0)2 627 42 11"
          },
          {"city":"Paris",
           "country":"France",
           "email": "valhuber@nhn.fr",
           "postcode":"75000",
           "street": " 57 Rue Cuvier",
            "phone":"+33 01 40 79 56 01 / 54 79 "
          },
          {"city":"Leiden",
           "country":"Netherlands",
           "email": "contact@naturalis.nl",
           "postcode":"2333 CR Leiden",
           "street": "Darwinweg 2"
          },
          {"city":"London",
           "country":"United Kingdom",
           "email": "info@mfn.berlin",
           "postcode":"SW 7 5BD",
           "street": "Cromwell Rd, South Kensington, "
          },
          
          
          ]

global_generator=None
started=False
iCols=1
es=None

def lorem_ipsum(field,idx):
    return field+ " " + str(idx) +" Section 1.10.32 du \"De Finibus Bonorum et Malorum\" de Ciceron (45 av. J.-C.) \r\n Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?"

def lorem_ipsum_short(field,idx):
    return field+ " " + str(idx) +" Short text"
    
def get_url():
    return  "https://en.wikipedia.org/wiki/Consortium_of_European_Taxonomic_Facilities"         

def create_person(iter=1):
    returned=[]
    returned_2={}
    for i in range(1,iter+1):
        tmp_array={}
        tmp_array["contact_type"]="contact type"+str(i)
        tmp_array["email"]="test_"+str(i)+"cetaf.org"
        tmp_array["name"]="Name"+str(i)
        tmp_array["name"]="Name Surname"+str(i)
        tmp_array["phone"]="0032 7777 "+str(i)
        tmp_array["title"]="Dr."
        returned.append(tmp_array)       
    returned_2["contact_person"]=returned
    json_tmp=json.dumps(returned_2)
    return json_tmp
    

#+ iter 
def coll_generator(iter_total=15):
    i=0
    for main_coll, subs in coll_struct.items(): 
        print(main_coll)
        for sub_coll in subs:
            yield [main_coll, sub_coll]

def create_coll(museum, coll, parent_coll=None):
    global iCols
    global es
    returned_2={}
    returned_2["main_type"]="collection"
    returned_2["url_id"]=URL_ID+"/collection/"+str(iCols)
    returned_2["parent_institution"]=museum
    global list_paths
    if parent_coll:
        returned_2["list_parent_collections"]=list_paths[parent_coll]+ [parent_coll]
        returned_2["full_path"]=museum+"/"+parent_coll+"/"+coll
        list_paths[coll]=returned_2["list_parent_collections"]
    else:
        returned_2["list_parent_collections"]=[museum]
        returned_2["full_path"]=museum+"/"+coll
        list_paths[coll]=returned_2["list_parent_collections"]
    returned={}
    returned["collection_name"]=coll
    returned["collection_description"]=lorem_ipsum("Description of collection",iCols)
    
    coverage={}
    coverage["countries_and_areas"]=[{"area_type":"country", "area_identifier":{"area_identifier_system":"iso3166", "area_identifier_value":"be" }, "area_name":"Belgium"},{"area_type":"country", "area_name":"Vlaams Brabant"},{"area_type":"country", "area_name":"Hainaut"}]
    
    if not parent_coll:
        coverage["taxonomic_coverage_main_category"]=coll
    else:
        coverage["taxonomic_coverage_main_category"]=parent_coll
        coverage["taxonomic_coverage_sub_category"]=coll
    coverage["temporal_scope"]={"gte":1800,"lte":2000}
    returned["coverage_fields"]=coverage
    
    size={}
    size["mids_level"]=2
    size["primary_types_count"]=iCols
    size["specimens_count"]=iCols*1000
    size["units_count"]=iCols*100
    returned["description_fields"]=size
    
    returned_2["natural_history_collection"]=returned
    relation={}
    relation["name"]="root"
    if parent_coll:
        relation["parent"]=museum+"/"+parent_coll
    else:
        relation["parent"]=museum
    print(relation)
    
    returned_2["manager_head_of_collection"]={"manager_title":"Dr.", "manager_name":"Syd Barrett", "manager_email":"syd.barrett@cetaf.be", "manager_research_fields":['Mycology','Anthropology']}
    returned_2["parent_relationship"]=relation
    print("CREATE COLL")
    global INDEX_NAME
    print("created "+returned_2["full_path"])
    es.index(index=INDEX_NAME, doc_type= "_doc",id=returned_2["full_path"], body=returned_2, routing=relation["parent"])
    if(coll=="Vascular plants"):
        for i in range(0,3):
            print("CREATE = "+coll+"sub_col"+str(i)+ " with parent "+parent_coll+"/"+coll)
            list_paths[parent_coll+"/"+ coll]=[parent_coll]
            create_coll(museum, coll+"sub_col"+str(i),parent_coll+"/"+ coll)
            #raise Exception("debug") 
            
            
def init_main_coll(museum):
    for main_coll, subs in coll_struct.items():
        create_coll(museum, main_coll)
        
def create_collection(museum, iter_total=18, iter_in_level=3):
    global started
    global global_generator
    global iCols
    if not  started:
        global_generator=coll_generator(iter_total)
        started=True       
    for i in range(0,iter_total):
        try:         
            cols=next(global_generator)
            print(cols)
            create_coll(museum, cols[1], cols[0])
        except StopIteration:
            print("REWIND")
            global_generator=coll_generator(iter_total)
        print(iCols)
        iCols=iCols+1 
        
         
def create_institution(iter=1):
    returned=[]
   
    for i in range(1,iter+1):
        returned_2={}
        tmp_array={}
        tmp_array["institution_name"]="Museum of Natural History "+str(i)
        tmp_array["institution_description"]="The Museum of Natural Sciences of Belgium "+str(i)
        
        identification={}
        identification["country_iso3166"]="be"
        identification["country_en"]="Belgium"
        identification["unique_acronym"]="BE-NHM"+str(i)
        identification["grscicoll_code"]="RBINS"
        identification["wikidata_id"]="Q16665660"
        identification["grid_id"]="grid.20478.39"
        
        original_name_1={}
        original_name_1["iso639"]="fr"
        original_name_1["lang"]="French"
        original_name_1["lang"]="Institut Royal des Sciences Naturelles de Belgique "+str(i)
        original_name_2={}
        original_name_2["iso639"]="nl"
        original_name_2["lang"]="Dutch"
        original_name_2["lang"]="Koninklijk Belgisch Instituut voor Natuurwetenschappen "+str(i)
        
        identification["original_name"]=[original_name_1, original_name_2]
        
        tmp_array["identification_fields"]=identification
        
        tmp_array["annual_report_fields"]=lorem_ipsum("Annual report",1)
        tmp_array["annual_report_fields_url"]=get_url()
        tmp_array["dashboard"]=lorem_ipsum("dashboard report",1)
        tmp_array["dashboard_url"]=get_url()
        tmp_array["institution_description"]=lorem_ipsum("Description",1)
        
        finances={}
        finances["funding_sources_external_euros"]=lorem_ipsum_short("External finance",1)
        finances["funding_sources_internal_euros"]=lorem_ipsum_short("Internal finance",1)
        finances["general_description"]=lorem_ipsum("General description finance",1)
        finances["operating_budget_euros"]=5000000
        finances["other_informations_operating_budget"]=lorem_ipsum("Finance information",1)
        tmp_array["finances"]=finances
        
        interest={}
        interest["current_topics_of_interest"]=["Field work", "Ecology", "Development Cooperation", "Conservation of protected areas", "Caribous"]
        interest["future_topics_of_interest"]=["Space travel", "space rock", "Electric cars", "Trap music for fast food animation"]
        interest["general_description"]=lorem_ipsum("General description interest",i)
        
        links={}
        link_1={}
        link_1["institution_link_type"]="wikipedia"
        link_1["institution_url"]="https://en.wikipedia.org/wiki/Consortium_of_European_Taxonomic_Facilities"
        
        link_2={}
        link_2["institution_link_type"]="wikidata"
        link_2["institution_url"]="https://www.wikidata.org/wiki/Q5163385"        
        tmp_array["institution_links"]=[link_1, link_2]
        
        
        tmp_array["interest_involvement_cetaf"]=interest
        
        tmp_array["main_areas_of_taxonomic_expertise"]=["Vertebrates", "Heterocera","Hymenoptera","Rhopalocera", "Echinodermata"]
        tmp_array["institution_name"]="Museum TEST"+str(i)
        
        research={}
        research["general_description"]=lorem_ipsum("General description research",1)
        research["research_fields"]=["Zoology", "Anthroplogy", "Social sciences", "History of arts"]
        research_programs=[]
        for j in range (1,4):
            research_program_tmp={}
            research_program_tmp["contribution_description"]=lorem_ipsum("General description research program",j)
            links={}
            link_1={}
            link_1["research_link_description"]="wikipedia"
            link_1["research_url"]="https://en.wikipedia.org/wiki/Consortium_of_European_Taxonomic_Facilities"
            
            link_2={}
            link_2["research_link_description"]="wikidata"
            link_2["research_url"]="https://www.wikidata.org/wiki/Q5163385"        
            research_program_tmp["research_links"]=[link_1, link_2]
            research_program_tmp["partner_institutions"]=["Naturalis", "MNHN", "NFM", "NHM"]
            research_program_tmp["program_name"]="ICEDIG.EU"
            research_program_tmp["workpackage_name"]=["WP4.3", "WP1.7"]
            research_programs.append(research_program_tmp)
        research["research_programs"]=research_programs    
        tmp_array["research"]=research
        
        #############
        organisation={}
        organisation["address"]=addresses[random.randrange(0,len(addresses))]    
    
        returned_2["organisation"]=organisation
        #############
        returned_2["main_type"]="institution"
        returned_2["url_id"]=URL_ID+str(i)
        returned_2["direct_children"]=[]
        returned_2["full_path"]=tmp_array["institution_name"]
        returned_2["cetaf_institution"]=tmp_array
        relation={}
        relation["name"]="root"
        relation["parent"]="null"
        returned_2["parent_relationship"]=relation
       
        
        returned.append(returned_2)
    
        
    #json_tmp=json.dumps(returned)
    return returned

    
    
def parse():
    print("test")
    tmp_person=create_person(iter=6)
    print(tmp_person)
    tmp_institutions=create_institution(160)
    print(tmp_institutions)
    global es
    es =  Elasticsearch(
        ['ursidae.rbins.be'],       
        use_ssl = False,
        port=9200,
    )
    for inst in tmp_institutions:
        #print(inst)
        global INDEX_NAME
        es.index(index=INDEX_NAME, doc_type= "_doc",id=inst["cetaf_institution"]["identification_fields"]["unique_acronym"], body=inst, routing="null")
        init_main_coll(inst["cetaf_institution"]["identification_fields"]["unique_acronym"])
        create_collection(inst["cetaf_institution"]["identification_fields"]["unique_acronym"])
    

if __name__ == "__main__":
    # execute only if run as a script
    parse()
    