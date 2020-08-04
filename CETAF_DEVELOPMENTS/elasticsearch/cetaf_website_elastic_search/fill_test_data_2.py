import json
from elasticsearch import Elasticsearch
import random

INDEX_NAME_INSTITUTIONS="cetaf_passport_institutions"
INDEX_NAME_COLLECTIONS="cetaf_passport_collections"
INDEX_NAME_FACILITIES="cetaf_passport_facilities"
INDEX_NAME_EXPERTISES="cetaf_passport_expertises"
URL_ID="http://collections.naturalsciences.be/cpb/nh-collections/countries/belgium/be-rbins/"
countries=['Belgium', 'Netherlands', 'United Kingdom', 'Germany']
countries_iso=['be', 'nl', 'gb', 'de']
i_countries=1

coll_struct={}
coll_struct["Botany"]=["Vascular plants","Bryophytes (mosses)","Algae" ]
coll_struct["Mycology"]=["Fungi and lichens" ]
coll_struct["Zoology Invertebrates"]=["Arthropods - insects", "Arthropods - arachnids", "Arthropods - crustaceans & myriapods", "Mollusks (bivalves, gastropods, cephalopods)", "Cnidaria (corals, jellyfish, anemones)", "Porifera (sponges)", "Other (other taxonomic groups)"]
coll_struct["Zoology Vertebrates"]=["Fishes", "Amphibians", "Reptiles", "Birds", "Mammals"]
list_paths={}

research_fields=["Zoology", "Anthroplogy", "Social sciences", "History of arts"]

facility_list=["Genetic lab", "Histology room", "X Ray scanner", "3D Capture lab"]
tool_list=["Sequencer", "3D Printer", "X Ray scanner", "Microscope", "Parallel calculation machine"]
protocol_list=["PCR", "Genotyping by sequencing", "De Novo Assembly"]


addresses=[{"city":"Brussel",
           "country":"Belgium",
           "email": "info@naturalsciences.be",
           "postcode":"1000",
           "street": "Rue Vautier",
           "phone":"+32 (0)2 627 42 11"
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
           {"city":"Berlin",
           "country":"Germany",
           "email": "info@mfn.berlin",
           "postcode":"SW 7 5BD",
           "street": "Invalidenstraße 43"
          }
          
          ]

global_generator=None
started=False
iCols=1
iFacility=1
es=None

def lorem_ipsum(field,idx):
    return field+ " " + str(idx) +" Section 1.10.32 du \"De Finibus Bonorum et Malorum\" de Ciceron (45 av. J.-C.) \r\n Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?"

def lorem_ipsum_short(field,idx):
    return field+ " " + str(idx) +" Short text"
    
def get_url():
    return  "https://en.wikipedia.org/wiki/Consortium_of_European_Taxonomic_Facilities"         

def create_facility(museum):
    global iFacility
    iF=random.randrange(0, len(facility_list)-1)
    iT=random.sample(range(0, len(tool_list)-1), 2)
    iP=random.randrange(0, len(protocol_list)-1)
    returned_2={}
    returned_2["to_parent_institution"]=museum
    returned_2["facility_name"]=facility_list[iF]
    returned_2["available_tools"]=[tool_list[iT[0]], tool_list[iT[1]]]
    returned_2["available_protocols"]=protocol_list[iP]
    returned_2["facility_description"]=lorem_ipsum("Facility description", iFacility)
    returned_2["facility_address"]=addresses[random.randrange(0,len(addresses))]
    contact={}    
    contact["contact_description"]="Peson to contact to hire the lab"
    contact["contact_email"]="patrick.juvey@yahoo.fr"
    contact["contact_name"]="Patrick juvet"
    contact["contact_phone"]="+34 444"
    contact["contact_title"]="Dr."
    contact["contact_type"]="Scientific assistant"
    returned_2["contact"]=contact    
    returned_2["url_id"]=returned_2["url_id"]=URL_ID+"/facility/"+str(iFacility)
    returned_2["full_path"]=museum+"/"+returned_2["facility_name"]
    iFacility=iFacility+1
    global INDEX_NAME_FACILITIES
    es.index(index=INDEX_NAME_FACILITIES, doc_type= "_doc",id=returned_2["full_path"], body=returned_2)

#+ iter 
def coll_generator(iter_total=15):
    i=0
    for main_coll, subs in coll_struct.items(): 
        print(main_coll)
        for sub_coll in subs:
            yield [main_coll, sub_coll]
            
            
            
def init_main_coll(museum, museum_name ):
    for main_coll, subs in coll_struct.items():
        create_coll(museum, museum_name, main_coll)

        
def create_collection(museum, museum_name, iter_total=18, iter_in_level=3):
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
            create_coll(museum,museum_name,  cols[1], cols[0])
        except StopIteration:
            print("REWIND")
            global_generator=coll_generator(iter_total)
        print(iCols)
        iCols=iCols+1 
        

def create_coll(museum, museum_name,  coll, parent_coll=None):
    global iCols
    global es
    returned_2={}
    returned_2["url_id"]=URL_ID+"/collection/"+str(iCols)
    returned_2["to_parent_institution"]=museum
    global list_paths
    if parent_coll:
        returned_2["to_all_parent_collections"]=list_paths[parent_coll]+ [parent_coll]        
        returned_2["full_path"]=museum+"/"+parent_coll+"/"+coll
        returned_2["to_parent_collection"]='/'.join(returned_2["full_path"].split("/")[:-1])
        list_paths[coll]=returned_2["to_all_parent_collections"]
    else:
        returned_2["to_all_parent_collections"]=[museum]
        returned_2["full_path"]=museum+"/"+coll
        list_paths[coll]=returned_2["to_all_parent_collections"]
        

    returned_2["collection_name"]=coll
    returned_2["institution_name"]=museum_name
    #returned_2["collection_description"]=lorem_ipsum("Description of collection",iCols)
    
    coverage={}
    coverage["countries_and_areas"]=[{"area_type":"country", "area_identifier":{"area_identifier_system":"iso3166", "area_identifier_value":"be" }, "area_name":"Belgium"},{"area_type":"country", "area_name":"Vlaams Brabant"},{"area_type":"country", "area_name":"Hainaut"}]
    
    if not parent_coll:
        coverage["taxonomic_coverage_main_category"]=coll
    else:
        coverage["taxonomic_coverage_main_category"]=parent_coll
        coverage["taxonomic_coverage_sub_category"]=coll
    coverage["temporal_scope"]={"gte":1800,"lte":2000}
    coverage["stratigraphical_coverage_text"]=lorem_ipsum("stratigraphical_coverage_text",iCols)
    coverage["stratigraphical_subdivision"]=lorem_ipsum_short("stratigraphical_coverage_text",iCols)
    returned_2["coverage_fields"]=coverage
    
    size={}
    size["mids_level"]=random.randrange(1,3)
    size["primary_types_count"]=iCols
    size["specimens_count"]=iCols*1000
    size["units_count"]=iCols*100
    returned_2["size_and_digitisation_fields"]=size
    
    returned_2["manager_head_of_collection"]={"manager_title":"Dr.", "manager_name":"Syd Barrett", "manager_email":"syd.barrett@cetaf.be", "manager_research_fields":['Mycology','Anthropology']}
    
    
    returned_2["url_id"]=URL_ID+'/collection/'+str(iCols)
    print("CREATE COLL")
    global INDEX_NAME_COLLECTIONS
    print("created "+returned_2["full_path"])
    es.index(index=INDEX_NAME_COLLECTIONS, doc_type= "_doc",id=returned_2["full_path"], body=returned_2)
    if(coll=="Vascular plants"):
        for i in range(0,3):
            print("CREATE = "+coll+"sub_col"+str(i)+ " with parent "+parent_coll+"/"+coll)
            list_paths[parent_coll+"/"+ coll]=[parent_coll]
            create_coll(museum, coll+"sub_col"+str(i),parent_coll+"/"+ coll)
            #raise Exception("debug")     
         
def create_institution(iter=1):
    returned=[]
    global i_countries
    i_countries=0
    for i in range(1,iter+1):
        returned_2={}
        
        i_countries=(i_countries + 1 ) % len(countries)
        tmp_array={}
        country=countries[i_countries-1]
        iso_tmp=countries_iso[i_countries-1]
        tmp_array["institution_name"]="Museum of Natural History "+str(i)
        tmp_array["institution_description"]="The Museum of Natural Sciences of Belgium "+str(i)
        returned_2["url_id"]=URL_ID+str(i)
        print(country)
        print(iso_tmp)
        returned_2["country_iso3166"]="be"
        returned_2["country_en"]="Belgium"
        returned_2["institution_name"]="Natural Science Institute n°"+str(i)
        identification={}
        
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
        
        returned_2["identification_fields"]=identification
        
        returned_2["full_path"]=identification["unique_acronym"]
        
        contact1={}
        contact1["contact_type"]="Organizer of the Summer school"
        contact1["contact_email"]="test1@gmail.com"
        contact1["contact_name"]="Kim Jacobsen"
        contact1["contact_phone"]="+32 XXXXX"
        contact1["contact_title"]="Dr."
        
        contact2={}
        contact2["contact_type"]="Organizer of training stages"
        contact2["contact_email"]="test2@gmail.com"
        contact2["contact_name"]="Muriel Van Nuffel"
        contact2["contact_phone"]="+32 XXXXX"
        contact2["contact_description"]="On maternity leave"
        
        representative={}
        representative["dir_rep_category"]="CETAF Deputy"
        representative["dir_rep_description"]="Elected since 2016, Mr Smith is XXXXXXX and WWWWW"
        representative["dir_rep_email"]="ian.smith@yahoo.fr"
        representative["dir_rep_name"]="Ian Smith"
        representative["dir_rep_phone"]="+34 444"
        representative["dir_rep_position"]="Executive Director"
        representative["dir_rep_title"]="Dr."
        returned_2["director_or_legal_representative"]=representative
        
        returned_2["institution_description"]=lorem_ipsum("Institution description",i)
        
        returned_2["contact"]=[contact1, contact2]
        
        returned_2["institution_address"]=addresses[random.randrange(0,len(addresses))]    
        
        research={}
        research["general_description"]=lorem_ipsum("General description research",1)
        ir=random.sample(range(0, 3), 3)
        research["research_fields"]=[research_fields[ir[0]], research_fields[ir[1]], research_fields[ir[2]]]
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
        returned_2["research"]=research
        
        
        returned.append(returned_2)
        

    
        
    #json_tmp=json.dumps(returned)
    return returned

    
    
def parse():
    print("test")
   
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
        global INDEX_NAME_INSTITUTIONS
        es.index(index=INDEX_NAME_INSTITUTIONS, doc_type= "_doc",id=inst["identification_fields"]["unique_acronym"], body=inst)
        init_main_coll(inst["identification_fields"]["unique_acronym"], inst["institution_name"])
        create_collection(inst["identification_fields"]["unique_acronym"], inst["institution_name"])
        create_facility(inst["identification_fields"]["unique_acronym"])
        create_facility(inst["identification_fields"]["unique_acronym"])
   
    

if __name__ == "__main__":
    # execute only if run as a script
    parse()
    
