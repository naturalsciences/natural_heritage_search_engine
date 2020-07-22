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
    
    collection_portal_fields1={}
    collection_portal_fields1["collection_page"]="Global search portal"
    collection_portal_fields1["collection_page_url"]="http://www.naturalheritage.be/"
    
    collection_portal_fields2={}
    collection_portal_fields2["collection_page"]="collection portal"
    collection_portal_fields2["collection_page_url"]="http://www.naturalsciences.be/"
    returned_2["collection_portal_fields"]=[collection_portal_fields1, collection_portal_fields2]
    
    description_fields={}
    description_fields["accession_specimens"]=lorem_ipsum("accession_specimens1", iCols )
    description_fields["collection_statistics"]="<table name='results1' id='results1' class='results'><tbody><tr><th>collection name</th><th>nb database records</th><th>nb physical specimens low</th><th>nb physical specimens high</th></tr><tr><td>Alex Fain's Acari Collection</td><td>63045</td><td>81013</td><td>81251</td></tr><tr><td>Alexis Robert</td><td>32</td><td>89</td><td>89</td></tr><tr><td>Algemeen</td><td>899</td><td>4873</td><td>4873</td></tr><tr><td>Arsène Fouassin</td><td>3997</td><td>5686</td><td>5686</td></tr><tr><td>Belgian Ceratopogonidae Collection</td><td>884</td><td>1573</td><td>1573</td></tr><tr><td>Belgian Coleoptera Collection</td><td>5180</td><td>258057</td><td>258057</td></tr><tr><td>Belgian Heterocera Collection</td><td>3007</td><td>120784</td><td>120784</td></tr><tr><td>Belgian Mecoptera Collection</td><td>5</td><td>543</td><td>543</td></tr><tr><td>Belgian Megaloptera Collection</td><td>4</td><td>241</td><td>241</td></tr><tr><td>Belgian Neuroptera Collection</td><td>63</td><td>1456</td><td>1456</td></tr><tr><td>Belgian Orthoptera Collection</td><td>179</td><td>5300</td><td>5300</td></tr><tr><td>Belgian Rhopalocera Collection</td><td>1507</td><td>51332</td><td>51332</td></tr><tr><td>BE-RBINS Entomology</td><td>1</td><td>1</td><td>1</td></tr><tr><td>Chapelle J.</td><td>6</td><td>6</td><td>6</td></tr><tr><td>Collection M. Bequaert</td><td>130</td><td>190</td><td>190</td></tr><tr><td>Collection M. Goetghebuer</td><td>256</td><td>387</td><td>387</td></tr><tr><td>Collection of protected insects</td><td>8</td><td>8</td><td>8</td></tr><tr><td>Collection Voyage of H. R. H. the Prince Leopold (1929)</td><td>963</td><td>1614</td><td>1614</td></tr><tr><td>Collection Voyage of H. R. H. the Prince Leopold (1932)</td><td>703</td><td>1688</td><td>1688</td></tr><tr><td>Coll Fain /1</td><td>83</td><td>91</td><td>91</td></tr><tr><td>Derenne Emile</td><td>1195</td><td>4976</td><td>4976</td></tr><tr><td>Didactic collection</td><td>13</td><td>13</td><td>13</td></tr><tr><td>Diptera Belgium</td><td>6180</td><td>6241</td><td>6241</td></tr><tr><td>Diptera General</td><td>15230</td><td>20537</td><td>20537</td></tr><tr><td>Drumont Alain</td><td>47</td><td>73</td><td>73</td></tr><tr><td>External Xylobiontes Collection</td><td>1</td><td>1</td><td>1</td></tr><tr><td>Galant M.</td><td>23</td><td>38</td><td>38</td></tr><tr><td>General Araneae Collection</td><td>1275</td><td>1710</td><td>1710</td></tr><tr><td>General Coleoptera Collection</td><td>15570</td><td>386694</td><td>386694</td></tr><tr><td>General Collection</td><td>2797</td><td>2797</td><td>2797</td></tr><tr><td>General Heterocera Collection</td><td>307</td><td>608</td><td>608</td></tr><tr><td>General Orthoptera Collection</td><td>1712</td><td>38432</td><td>38432</td></tr><tr><td>General Rhopalocera Collection</td><td>12480</td><td>152617</td><td>152617</td></tr><tr><td>Guilleaume Félix</td><td>207</td><td>363</td><td>363</td></tr><tr><td>Hennuy J. J.</td><td>14</td><td>22</td><td>22</td></tr><tr><td>H. M. King Leopold III</td><td>658</td><td>949</td><td>949</td></tr><tr><td>H. M. Queen Elisabeth (Brazilian Lepidoptera)</td><td>1483</td><td>1556</td><td>1556</td></tr><tr><td>Jacobs</td><td>2</td><td>3</td><td>3</td></tr><tr><td>J.P. Smeekens</td><td>9</td><td>203</td><td>203</td></tr><tr><td>Leroux</td><td>458</td><td>1054</td><td>1054</td></tr><tr><td>Mal Noël</td><td>28</td><td>51</td><td>51</td></tr><tr><td>Maquet Daniel</td><td>19</td><td>68</td><td>68</td></tr><tr><td>M.-E. de Selys-Longchamps</td><td>2131</td><td>6792</td><td>6792</td></tr><tr><td>Miessen Geoffrey</td><td>73</td><td>114</td><td>114</td></tr><tr><td>Muret P.</td><td>8</td><td>12</td><td>12</td></tr><tr><td>RBINS Xylobiontes Collection</td><td>18279</td><td>208018</td><td>208018</td></tr><tr><td>Reference collection</td><td>54</td><td>54</td><td>54</td></tr><tr><td>Ronald Brabant</td><td>4085</td><td>4984</td><td>4984</td></tr><tr><td>Supplementen</td><td>714</td><td>2353</td><td>2353</td></tr><tr><td>Types Virtual Collections</td><td>3715</td><td>4164</td><td>4164</td></tr><tr><td>Van Dorsselaer</td><td>118</td><td>5002</td><td>5002</td></tr><tr><td><b>TOTAL</b></td><td><b>169837</b></td><td><b>1385431</b></td><td><b>1385669</b></td></tr></tbody></table>"   

    description_fields["genetic_repository"]=["Barcode of life", "GenBank"]
    description_fields["genetic_repository_link"]=["https://ibol.org/", "https://www.ncbi.nlm.nih.gov/genbank/"]
    description_fields["other_size_indicators"]="Required physical storage space : 240 m3"
    description_fields["outstanding_collection_features"]="Holotype of Afropavo (Congolese Peacock)"
    returned_2["description_fields"]=description_fields
    
    edu_contact1={}
    edu_contact1["edu_contact_type"]="Organizer of the Summer school"
    edu_contact1["edu_email"]="test1@gmail.com"
    edu_contact1["edu_name"]="Kim Jacobsen"
    edu_contact1["edu_phone"]="+32 XXXXX"
    edu_contact1["edu_title"]="Dr."
    
    edu_contact2={}
    edu_contact2["edu_contact_type"]="Registration officer"
    edu_contact2["edu_email"]="test2@gmail.com"
    edu_contact2["edu_name"]="Ian Smith"
    edu_contact2["edu_phone"]="+32 4XXXX"
    
    education={}
    education["education_general_description"]="Summer school on the Electric Discharge organs of fishes"
    education_detail={}
    education_detail["training_online_or_presential"]="presential"
    education_detail["training_type"]="summer school (No ECTS)"
    education["training"]=education_detail
    education["contact_person"]=[edu_contact1, edu_contact2]
    returned_2["education"]=education
    
    facility1={}
    facility1["available_tools"]=["PCR", "Restriction ensymes for DNA barcode", "4 core machines", "TASSEL GBS software"]
    facility1["facility_description"]="JEMU genetic laboratorys"
    facility1["list_of_facilities"]=[ "Fozen storage room", "Computer room"]
    facility1["list_of_laboratories"]=["PCR room", "Molecular analysis room"]
    
    facility2={}
    facility2["available_tools"]=["Miscroscope", "X-Ray machine"]
    facility2["facility_description"]="Ichtyological room"
    facility2["list_of_facilities"]=[ "Storage room", "Training room"]
    facility2["list_of_laboratories"]=["Meristic unit room"]
    returned_2["facility"]=[facility1, facility2]
    
    mngr_contact={}
    mngr_contact["manager_position"]="Head of collection"
    mngr_contact["manager_email"]="test1@gmail.com"
    mngr_contact["manager_name"]="Ernst Lubitsch"
    mngr_contact["manager_phone"]="+32 XXXXX"
    mngr_contact["manager_title"]="Dr."
    mngr_contact["manager_research_fields"]=["Anthropology","Political sciences", "Esthetics", "Sociology" ]
    returned_2["manager_head_of_collection"]=mngr_contact
    
    natural_history_collection={}
    natural_history_collection["abstract"]=lorem_ipsum("Abstract of collection",iCols)
    natural_history_collection["acquisition_source"]=["Donation", "Field work", "Merging of institution collections"]
    natural_history_collection["codes"]=["COL1-NHM", "10.1000/xyz123"]
    contact1={}
    contact1["adm_contact_type"]="Secretary of Vertrebrate Department"
    contact1["adm_email"]="test1@gmail.com"
    contact1["adm_name"]="Paul Canon"
    contact1["adm_phone"]="+32 XXXXX"
    administration_field={}
    administration_field["contact_person"]=contact1
    administration_field["legal_property"]="Collection owned by XXX"
    administration_field["status"]="Free access for academic use"
    natural_history_collection["administration_field"]=administration_field
    

    staff1={}
    staff1["staff_collection_role"]="Researcher in entomology"
    staff1["staff_curatorial_role"]="Scientific curator"
    staff1["staff_degree_msc_discipline"]="Agrononmy"
    staff1["staff_degree_msc_title"]="Economic impact of the introduction of lobster in technical mangroves"
    staff1["staff_description"]=lorem_ipsum_short("staff 1", iCols)
    staff1["staff_expertise_description"]="Agronomy and taxonomi"
    staff1["staff_expertise_domain"]=["Ecology of mangrove", "ecology of small lakes"]
    staff1["staff_expertise_geography"]="Adriatic sea"
    staff1["staff_name"]="Jacqueline Robson"
    staff1["staff_full_time_equivalent_pc"]=90
    si1={}
    si1["value"]="0000-0002-0626-538X"
    si1["system"]="ORCID"
    staff1["staff_identifiers"]=si1
    
    staff2={}
    staff2["staff_collection_role"]="Researcher in entomology"
    staff2["staff_curatorial_role"]="Scientific curator"
    staff2["staff_degree_msc_discipline"]="Agrononmy"
    staff2["staff_degree_msc_title"]="Economic impact of the introduction of lobster in technical mangroves"
    staff2["staff_description"]=lorem_ipsum_short("staff 1", iCols)
    staff2["staff_expertise_description"]="Agronomy and taxonomi"
    staff2["staff_expertise_domain"]=["Ecology of mangrove", "ecology of small lakes"]
    staff2["staff_expertise_geography"]="North Pacific coast"
    staff2["staff_name"]="John Mondale"
    staff2["staff_full_time_equivalent_pc"]=50
    si2={}
    si2["value"]="0000-0002-0626-540X"
    si2["system"]="ORCID"
    staff2["staff_identifiers"]=si2

    natural_history_collection["collection_staff"]=[staff1, staff2]
    returned_2["natural_history_collection"]=natural_history_collection

    
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
    
