curl -X PUT "localhost:9200/cetaf_passport?pretty" -H 'Content-Type: application/json' -d'
{
    "settings" : {
        "number_of_shards" : 1
    },
    "mappings" : {
         "properties":{
                "url_id": {
                    "type":"text"                   
                },
                "main_type":
                {
                   "type":"keyword" /*
                   institution, 
                   collection_group, 
                   natural_history_collection,
                   organisation,
                   facility,
                   relation_communication,
                   education_training,
                   interest_involvement,
                   finances,
                   research,
                   taxonomic_expertise
                   */     
                }
                ,
                "parent_relationship": {
                    "type":"join",
                    "relations":
                    {
                        "root":"detail",
                        "detail":"root"
                    }
                }
                ,
                "cetaf_institution":
                {
                   "type": "nested",
                    "properties":
                    {
                        
                                "name" :{
                                    "type": "text"
                                },
                                "description" : {
                                    "type": "text"
                                }
                            
                        ,
                        "identification_fields":
                        {
                            "type": "nested",
                            "properties":
                            {
                                "original_name":
                                {
                                    "type":"nested",
                                    "properties":
                                    {
                                        "iso639" :
                                        {
                                            "type": "keyword"
                                        },
                                        "lang" :
                                        {
                                            "type": "keyword"
                                        }, 
                                        "name" :
                                        {
                                            "type": "text"
                                        }
                                    }
                                },
                                "unique_acronym":
                                {
                                    "type": "keyword"
                                },
                                "grscicoll_code":
                                {
                                    "type": "keyword"
                                },
                                "wikidata_id":
                                {
                                    "type": "keyword"
                                },
                                "grid_id":
                                {
                                    "type": "keyword"
                                }
                            }
                        },

                                "dashboard":
                                {
                                    "type": "text"
                                },
                                "dashboard_url":
                                {
                                    "type": "keyword"
                                }
                            
                        ,

                        
                                "annual_report_fields":
                                {
                                    "type": "text"
                                },
                                "annual_report_fields_url":
                                {
                                    "type": "keyword"
                                }                        
                    
                    ,
                        "interest_involvement_cetaf":
                        {
                            "type":"nested",
                            "properties": 
                            {
                                "general_description":
                                {                            
                                    "type": "text"
                                },
                                "current_topics_of_interest":
                                {                            
                                    "type": "text"
                                },
                                "future_topics_of_interest":
                                {                            
                                    "type": "text"
                                }

                            }
                        },
                        "links":
                        {
                            "type":"nested",
                            "properties": 
                            {
                                "link_type":
                                {                            
                                    "type": "keyword"
                                    /*
                                    GBIF
                                    GrSCiCOLL
                                    ELVIS
                                    */
                                },
                                "url":
                                {                            
                                    "type": "keyword"
                                }

                            }
                        }
                        ,
                        "finances":
                        {
                            "type":"nested",
                            "properties": 
                            {
                                "general_description":
                                {                            
                                    "type": "text"
                                   
                                },
                                "operating_budget_euros":
                                {                            
                                    "type": "integer"
                                },
                                "funding_sources_internal_euros":
                                {                            
                                    "type": "text"
                                }
                                ,
                                "funding_sources_external_euros":
                                {                            
                                    "type": "text"
                                },
                                "other_informations_operating_budget":
                                {
                                    "type": "text"
                                }

                            }
                        }    
                        ,
                        "research":
                        {
                        
                            "type":"nested",
                            "properties": 
                            {
                                "general_description":
                                {                            
                                    "type": "text"
                                },
                                "research_fields":
                                {                            
                                    "type": "text"
                                },
                                "research_programs":
                                {                            
                                    "type": "nested",
                                    "properties":
                                    {
                                        "program_name":
                                        {
                                             "type": "keyword"
                                        },
                                        "contribution_description":
                                        {
                                             "type": "text"
                                        },
                                        "workpackage_name":
                                        {
                                             "type": "keyword"
                                        },
                                        "partner_institutions":
                                        {
                                             "type": "keyword"
                                        },
                                        "links":
                                        {
                                             "type": "nested",
                                             "properties":
                                             {
                                                "link_description":
                                                {
                                                    "type":"keyword"
                                                },
                                                "url":
                                                {
                                                    "type":"keyword"
                                                }
                                             }
                                        }
                                        
                                    }
                                }

                            }
                        
                        },
                        "main_areas_of_taxonomic_expertise":
                        {
                             "type":"text"
                        }
                    }
                 },
                  /////////////////COLLECTION 1
                "natural_history_collection":
                {
                    "type":"nested",
                    "properties": 
                    {
                        
                                    "name" :{
                                        "type": "text"
                                    },
                                    "description" : {
                                        "type": "text"
                                    }
                                    ,
                                    "abstract" : {
                                        "type": "text"
                                    }
                                    
                                
                            ,
                            "identification_fields":
                            {
                                        "type": "nested",
                                        "properties":
                                        {
                                            
                                                    "system":
                                                    {
                                                        "type":"keyword"
                                                        /*
                                                        DOI
                                                        HANDLE
                                                        ARK
                                                        LSID
                                                        Herbarias
                                                        */
                                                    },
                                                    "identifier":
                                                    {
                                                        "type":"keyword"
                                                    }
                                         }
                                            
                                        
                              },
                              "description_fields":
                              {
                                "type":"nested",
                                "properties":
                                {
                                    "units_count":
                                    {
                                        "type":"integer"
                                    },
                                    "specimens_count":
                                    {
                                        "type":"integer"
                                    },
                                    "primary_types_count":
                                    {
                                        "type":"integer"
                                    },
                                    "other_size_indicators":
                                    {
                                        "type":"text"
                                    },
                                    "owc_size_evaluation":
                                    {
                                        "type":"integer"
                                         /*
                                        1=0-10;
                                        2=11-100;
                                        3=101-1000;
                                        4=1001-10000;
                                        5=10001-100000;
                                        6=100001-1000000;
                                        7=1000001-10000000;
                                        8>10000000
                                        */
                                    }
                                    
                                }
                              },
                              "coverage_fields":
                              {
                                "type":"nested",
                                "properties":
                                {
                                    "taxonomic_coverage":
                                    {
                                        "type":"text"
                                    },
                                    "functional_group":
                                    {
                                        "type":"text"
                                    },
                                    "temporal_scope":
                                    {
                                        "type": "date_range", 
                                        "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd"
                                    }    
                                    ,
                                    "collecting_period_text":
                                    {
                                        "type": "text"
                                    }
                                    ,
                                    
                                            "geographical_coverage_coverage_text":
                                            {
                                                "type":"text"
                                            }
                                            ,
                                            "geographical_coverage_bbox":
                                            {
                                                "type":"geo_shape"
                                            },
                                            "geographical_coverage_link":
                                            {
                                                "type":"keyword"
                                            }
                                            ,
                                            "countries_and_areas":
                                            {
                                                "type":"nested",
                                                "properties":
                                                {
                                                    "area_type":
                                                    {
                                                        "type":"keyword"
                                                        /*country, region*/
                                                    },
                                                    "name":
                                                    {
                                                        "type":"text"
                                                    },
                                                    "identifier":
                                                    {
                                                        "type":"nested",
                                                        "properties":
                                                        {
                                                            "system":
                                                            {
                                                                "type":"keyword"                                    
                                                            },
                                                            "value":
                                                            {
                                                                "type":"keyword"
                                                            }
                                                           
                                                        }
                                                        
                                                    }
                                                }
                                            },
                                            
                                            "habitat":
                                            {
                                                "type":"nested",

                                                 "properties":
                                                  {      
                                                            "habitat_type":
                                                            {
                                                                "type":"keyword"
                                                                /*terrestrial, freshwater, marine, extraterrestrial*/
                                                            },
                                                            "pc":
                                                            {
                                                                "type":"integer"
                                                            },
                                                            "texte":
                                                            {
                                                                "type":"keyword"
                                                                /*
                                                                
                                                                    Terrestrial: Africa
                                                                    Terrestrial: Antarctic
                                                                    Terrestrial: Asia Temperate
                                                                    Terrestrial: Asia Tropical
                                                                    Terrestrial: Australasia
                                                                    Terrestrial: Europe
                                                                    Terrestrial: North America
                                                                    Terrestrial: Pacific
                                                                    Terrestrial: South America
                                                                    Terrestrial: World / NA
                                                                    etc...

                                                                */
                                                            }
                                                        }
                                                    

                                                    
                                                   
                                                   
                                                
                                                
                                            }
                                        
                                    ,

                                             "stratigraphical_coverage_text":
                                            {
                                                "type":"text"
                                            }
                                            ,
                                            "stratigraphy_link":
                                            {
                                                "type":"keyword"
                                            }
                                            ,
                                            "stratigraphical_subdivision":
                                            {
                                                "type":"keyword"
                                                /*
                                                    
                                                    Phanerozoic : Cenozoic
                                                    Phanerozoic : Cenozoic : Quaternary
                                                    Phanerozoic : Cenozoic : Quaternary : Holocene
                                                    Phanerozoic : Cenozoic : Quaternary : Pleistocene
                                                    Phanerozoic : Cenozoic : Neogene
                                                    Phanerozoic : Cenozoic : Neogene : Pliocene
                                                    Phanerozoic : Cenozoic : Neogene : Miocene
                                                    Phanerozoic : Cenozoic : Paleogene
                                                    Phanerozoic : Cenozoic : Paleogene : Oligocene
                                                    Phanerozoic : Cenozoic : Paleogene : Eocene
                                                    Phanerozoic : Cenozoic : Paleogene : Paleocene
                                                    Phanerozoic : Mesozoic
                                                    Phanerozoic : Mesozoic : Cretaceous
                                                    Phanerozoic : Mesozoic : Jurassic
                                                    Phanerozoic : Mesozoic : Triassic
                                                    Phanerozoic : Paleozoic
                                                    Phanerozoic : Paleozoic : Permian
                                                    Phanerozoic : Paleozoic : Carboniferous
                                                    Phanerozoic : Paleozoic : Devonian
                                                    Phanerozoic : Paleozoic : Silurian
                                                    Phanerozoic : Paleozoic : Ordovician
                                                    Phanerozoic : Paleozoic : Cambrian
                                                    Proterozoic
                                                    Archean
                                                    Hadean

                                                */
                                            }
                                        
                                    
                                }
                              },
                              "storage_fields":
                              {
                                "type":"nested",
                                "properties":
                                {
                                    "curation":
                                    {
                                        "type":"text"
                                    },
                                    
                                            "preparation_crosswak_description_standard":
                                            {
                                                "type":"keyword"
                                                /*
                                                  Dead: Botany: pressed and dried</element>
                                                  Dead: Botany: dried
                                                  Dead: Botany: fluid preserved
                                                  Dead: Botany: microscopic slides
                                                  Dead: Botany: cryopreserved / frozen -80&#176;C
                                                  Dead: Mycology: dried
                                                  Dead: Mycology: spore print
                                                  Dead: Mycology: fluid preserved
                                                  Dead: Mycology: microscopic slides
                                                  Dead: Mycology: cryopreserved / frozen -80&#176;C
                                                  Dead: Zoology Invertebrates: dried - pinned
                                                  Dead: Zoology Invertebartes: dried - assembled
                                                  Dead: Zoology Invertebrates: dried - not assembled
                                                  Dead: Zoology Invertebrates: fluid preserved
                                                  Dead: Zoology Invertebrates: microscopic slides
                                                  Dead: Zoology Invertebrates: cryopreserved / frozen -80&#176;C
                                                  Dead: Zoology Vertebrates: dried - assembled
                                                  Dead: Zoology Vertebrates: dried - not assembled
                                                  Dead: Zoology Vertebrates: fluid preserved
                                                  Dead: Zoology Vertebrates: microscopic slides
                                                  Dead: Zoology Vertebrates: cryopreserved / frozen -80&#176;C
                                                  Dead: Microbiology: dried
                                                  Dead: Microbiology: microscopic slides
                                                  Dead: Microbiology: cryopreserved DNA / RNA
                                                  Dead: Paleontological: botany
                                                  Dead: Paleontological: mycology
                                                  Dead: Paleontological: zoology vertebrates
                                                  Dead: Paleontological: zoology invertebrates
                                                  Dead: Paleontological: trace fossils
                                                  Dead: Paleontological: microscopic slides
                                                  Dead: Other
                                                  Living: Botany (in vivo)
                                                  Living: Botany (in vitro)
                                                  Living: Botany: Seeds &amp; germplasm (dormant)
                                                  Living: Mycology (in vitro)
                                                  Living: Zoology (in vivo)
                                                  Living: Zoology: germplasm (in vitro, dormant)
                                                  Living: Microbiology: cryopreserved / frozen -80&#176;C (in vitro)
                                                  Living: Microbiology: cell and tissue cultures (in vitro)
                                                  NA: Geology: Minerology
                                                  NA: Geology: Sample
                                                  NA: Geology: Microscopic slide
                                                  NA: Geology: Fluid
                                                  NA: Geology: Radioactive
                                                  NA: Geology: Other
                                                  NA: Extraterrestrial: Collected on Earth
                                                  NA: Extraterrestrial: Collected in space
                                                  NA: Not geo/biodiversity
                                                */
                                            },
                                            "preparation_treatment":
                                            {
                                                "type":"keyword"
                                                /*
                                                

                                                    Cryopreserved

                                                    Dried

                                                    Embedded

                                                    Fluid preserved

                                                    in vivo

                                                    in vitro

                                                    Pinned

                                                    Pressed

                                                    Skeletonized

                                                    Slide mount

                                                    Surface coating

                                                    Tanned

                                                    Wax Block

                                                */
                                                
                                            },
                                            "preparation_treatment_protocol":
                                            {
                                                "type":"text"
                                                
                                            }
                                        
                                    
                                    ,
                                    
                                            "conservation_text":
                                            {
                                                "type":"text"
                                            },
                                            "conservation_temperature":
                                            {
                                                "type":"keyword"
                                                /*
                                                

                                                        NA

                                                        No info

                                                        Ambient uncontrolled environment : outdoors

                                                        Ambient uncontrolled environment : indoors

                                                        4°c

                                                        -20°c

                                                        -80°c

                                                        -132°c -196°c

                                                                                                    */
                                            },
                                            "conservation_fluid":
                                            {
                                                "type":"keyword"
                                            },
                                            "conservation_container":
                                            {
                                                "type":"keyword"
                                                /*
                                                    Drawer
                                                    Drawer with cover
                                                    Jar
                                                    Box
                                                    Box with cover
                                                */
                                            },
                                            "conservation_container_material":
                                            {
                                                                                                                                                        "type":"keyword"
                                                /*
                                                    Ceramic
                                                    Glass
                                                    Metal
                                                    Plastic
                                                    Paper
                                                    Wood
                                                */
                                            },
                                            "label_media":
                                            {
                                                "type":"keyword"
                                                /*
                                                    NA
                                                    Paper
                                                    Paper acid-free
                                                    Synthetic film
                                                    Metallic label
                                                    Tissue labelOther
                                                */
                                            },
                                            "label_system":
                                            {
                                                "type":"keyword"
                                                /*
                                                    Handwritten
                                                    Type machine
                                                    Laser
                                                    Inkjet
                                                    Thermal direct
                                                    Thermal transfer
                                                    Engraved
                                                    Perforation
                                                    Other
                                                */
                                            },
                                            "label_system_if_other":
                                            {
                                                "type":"keyword"
                                            },
                                            "label_information":
                                            {
                                                "type":"text"
                                            }
                                        
                                    
                                }
                              }//
                              ,
                              "digitisation_fields":
                              {
                                "type":"nested",
                                "properties":
                                {
                                    "proportion_digitised":
                                    {
                                        "type":"keyword"
                                        /*
                                        

                                                0-10

                                                11-20

                                                21-30

                                                31-40

                                                41-50

                                                51-60

                                                61-70

                                                71-80

                                                81-90

                                                91-100

                                        */
                                    }
                                    ,
                                    "digitisation_strategy":
                                    {
                                        "type":"text"
                                    },
                                    "digitisation_list_url":
                                    {
                                        "type":"keyword"
                                    },
                                    "digitisation_list_texts":
                                    {
                                        "type":"text"
                                    }
                                    ,
                                    "imaging":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "target":
                                            {
                                                "type":"keyword"
                                                /*
                                                

                                                    overview

                                                    label

                                                    detailed

                                                    tray

                                                */
                                                
                                            },
                                            "technique":
                                            {
                                                "type":"keyword"
                                                /*
                                                

                                                    2D : scan

                                                    2D : picture

                                                    2D : picture macroscopy

                                                    2D : picture microscopy

                                                    2D : picture SEM

                                                    2D+ : photostacking

                                                    2d+ : multispectral

                                                    3D : surface

                                                    3D : surface : photogrammetry

                                                    3D : surface : scan

                                                    3D : surface : scan : laser

                                                    3D : surface : scan : laser microscopy

                                                    3D : surface : scan : structure ligth

                                                    3D : surface : scan : structure ligth microscopy

                                                    3D : internal

                                                    3D : internal : computed tomography

                                                    3D : internal : microcomputed tomography

                                                    3D+ : multispectral photogrammetry

                                                */
                                            },
                                            "calibration":
                                            {
                                                "type":"keyword"
                                                

                                                    /*internal scale

                                                    scaled

                                                    internal color chart

                                                    calibrated*/

                                            },
                                            "setup_description":
                                            {
                                                "type":"text"
                                            }
                                            ,
                                            "what":
                                            {
                                                "type":"keyword"
                                                /*
                                                

                                                        Drawer

                                                        Jar

                                                        Box

                                                        Transparent cover

                                                        Hard cover

                                                        MinigripUI: Unique identifier

                                                        PID: Persistent identifier (Stable URI, DOI, etc)

                                                        Record: creation date&time

                                                        Record: creator

                                                        Material type: BioGeo 1.

                                                        Material type: Storage 2.

                                                        Material type: GeoPaleo 3. (if applicable)

                                                        Deposited: Institute name

                                                        Deposited: Institute UI (if applicable)

                                                        Taxon: name(s)

                                                        Taxon: taxon name UI (CoL+)

                                                        Type status

                                                */
                                            }
                                            ,
                                            "who":
                                            {
                                                "type":"keyword"
                                                /*

                                                    Collector: name

                                                    Collector: UI

                                                    Collector: number (if present on specimen)
                                                */
                                            }
                                            ,
                                            "when":
                                            {
                                                "type": "date_range", 
                                                "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd"
                                            },
                                            "where":
                                            {
                                                "type":"keyword"
                                                /*

                                                    

                                                    Geography: region 4. (if present on specimen)

                                                    Geography: named locality (if present on specimen)

                                                    Geography: Latlong in decimal degrees (if present on specimen)

                                                    Geography: altitude/depth (if present on specimen)

                                                */
                                            },
                                            "varia":
                                            {
                                                "type":"text"
                                            }

                                        }
                                    }
                                }  
                              },
                              //valorisation
                              "valorisation":
                              {
                                    "type":"nested",
                                    "properties":
                                    {
                                       "type":
                                       {
                                            "type":"keyword"
                                            /*article or other*/
                                       },
                                       "dataset_role":
                                       {
                                            "type":"keyword"
                                            /*
                                               publication describing the dataset
                                               publication based onthe dataset
                                            */
                                       },
                                       "title":
                                       {
                                            "type":"text"
                                            
                                       },
                                       "description":
                                       {
                                            "type":"text"
                                            
                                       },
                                        "identification_fields":
                                        {
                                                    "type": "nested",
                                                    "properties":
                                                    {
                                                        
                                                                "system":
                                                                {
                                                                    "type":"keyword"
                                                                    /*
                                                                    DOI
                                                                    HANDLE
                                                                    ARK
                                                                    */
                                                                },
                                                                "identifier":
                                                                {
                                                                    "type":"keyword"
                                                                }
                                                     }
                                                        
                                                    
                                          },
                                        "dataset_citation":
                                        {
                                            "type":"text"
                                        },
                                        "licence":
                                        {
                                            "type":"keyword"
                                        },
                                        "licence_holder":
                                        {
                                            "type":"text"
                                        },
                                        "url":
                                        {
                                            "type":"keyword"
                                        }
                                     }
                                
                              }
                              ,
                              //collection staff
                              "collection_staff":
                              {
                                    "type":"nested",
                                    "properties":
                                    {
                                        "title":
                                        {
                                            "type":"keyword"
                                        },
                                        "description":
                                        {
                                            "type":"text"
                                        },
                                        "first_name":
                                        {
                                            "type":"text"
                                        },
                                        "last_name":
                                        {
                                            "type":"text"
                                        },
                                        "identifiers":
                                        {
                                            "type":"nested",
                                            "properties":
                                            {
                                                "system":
                                                {
                                                    "type":"keyword"
                                                    /*
                                                    ORCID, ...
                                                    */
                                                },
                                                "value":
                                                {
                                                    "type":"keyword"
                                                    /*
                                                    ORCID, ...
                                                    */
                                                }
                                            }
                                        }
                                        ,
                                        "status":
                                        {
                                             "type":"keyword"
                                             /*
                                              
                                                Permanent staff
                                                Long term contract
                                                Short term contract
                                                Volunteer

                                             */
                                        },
                                        "curatorial_role":
                                        {
                                            "type":"keyword"
                                             /*
                                              

                                                head of collections
                                                conservator
                                                curator
                                                collection manager
                                                preparator
                                                digitisation technician
                                                digitisation scientist
                                                encoder


                                             */
                                        },
                                        "collection_role":
                                        {
                                            "type":"keyword"
                                             /*
                                              

                                               
                                                    Collector
                                                    Owner
                                                    Identificator



                                             */
                                        },
                                        
                                                "degree_msc_discipline":
                                                {
                                                    "type":"keyword"
                                                    
                                                },
                                                                                                                                                        "degree_msc_title":
                                                {
                                                    "type":"keyword"
                                                    
                                                },
                                                
                                                "phd_msc_discipline":
                                                {
                                                    "type":"keyword"
                                                    
                                                },
                                                                                                                                                        "phd_msc_title":
                                                {
                                                    "type":"keyword"
                                                    
                                                }
                                            
                                        ,
                                        "link":
                                        {
                                            "type":"keyword"
                                        },
                                        "full_time_equivalent_pc":
                                        {
                                            "type":"keyword"
                                        },
                                        
                                                "expertise_domain":
                                                {
                                                    "type":"keyword"
                                                    /*
                                                    
                                                        Anthropology
                                                        Anthropology - Physical
                                                        Anthropology - Evolution
                                                        Anthropology - Archaeology
                                                        Anthropology - Ethnography
                                                        Anthropology - Social
                                                        Botany
                                                        Botany -
                                                        Geology
                                                        Geology - Mineralogy
                                                        Geology - Meteorites
                                                        Paleontology - Invertebrates
                                                        Paleontology - Micro-paleontology
                                                        Paleontology - Paleobotany
                                                        Paleontology - Vertebrates
                                                        Zoology - Entomology
                                                        Zoology - Invertebrates
                                                        Zoology - Vertebrates
                                                        Zoology - Vertebrates - Amphibians
                                                        Zoology - Vertebrates - Birds
                                                        Zoology - Vertebrates - Fishes
                                                        Zoology - Vertebrates - Mammals
                                                        Zoology - Vertebrates - Reptiles
                                                        ...

                                                    */
                                                },
                                                "expertise_geography":
                                                {
                                                    "type":"keyword"
                                                    /*
                                                    
                                                        Terrestrial: Africa
                                                        Terrestrial: Antarctic
                                                        Terrestrial: Asia Temperate
                                                        Terrestrial: Asia Tropical
                                                        Terrestrial: Australasia
                                                        Terrestrial: Europe
                                                        Terrestrial: North America
                                                        Terrestrial: Pacific
                                                        Terrestrial: South America
                                                        Terrestrial: World / NA
                                                        Freshwater: Africa
                                                        Freshwater: Antarctic
                                                        Freshwater: Asia Temperate
                                                        Freshwater: Asia Tropical
                                                        Freshwater: Australasia
                                                        Freshwater: Europe
                                                        Freshwater: North America
                                                        Freshwater: Pacific
                                                        Freshwater: South America
                                                        Freshwater: World / NA
                                                        Marine: Arctic Ocean
                                                        Marine: Indian Ocean
                                                        Marine: North Atlantic
                                                        Marine: South Atlantic
                                                        Marine: North Pacific
                                                        Marine: South Pacific
                                                        Marine: Southern Ocean
                                                        Marine: World / NA
                                                        Extraterrestrial

                                                    */
                                                }
                                                ,
                                                "expertise_description":
                                                {
                                                    "type":"text"
                                                }
                                            
                                        
                                        
                                    }
                              }
                              ,
                              "administration_field":
                              {
                                "type":"nested",
                                "properties":
                                {
                                    "status":
                                    {
                                        "type":"keyword"
                                       /*
                                       
                                            Public
                                            Private Institution
                                            Private person

                                       */
                                    },
                                    "legal_property":
                                    {
                                        "type":"text"
                                    },
                                    "contact_person":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "contact_type":
                                            {
                                                "type": "keyword"
                                                /*person institution*/
                                            },
                                            "title":
                                            {
                                                "type": "keyword"
                                            },
                                            "name":
                                            {
                                                "type": "keyword"
                                            },
                                            "phone":
                                            {
                                                "type": "keyword"
                                            },
                                            "email":
                                            {
                                                "type": "keyword"
                                            }                                            
                                        }
                                    }
                                }
                              }
                              ,
                              "codes":
                              {
                                    "type":"text"
                              },
                              "acquisition_source":
                              {
                                    "type":"keyword"
                                    /*                                    
                                        Field Collect
                                        Hand Gift
                                        Donation
                                        Purchase
                                        Exchange
                                        Desiderata
                                        Distraint
                                        Other
                                    */
                              },
                              "original_collectors":
                              {
                                    "type":"nested",
                                    "properties":
                                    {
                                        "full_name":
                                        {
                                           "type":"text" 
                                        },
                                        "identifier":
                                        {
                                            "type":"nested",
                                            "properties":
                                            {
                                                "system":
                                                {
                                                    "type":"keyword"                                    
                                                },
                                                "value":
                                                {
                                                    "type":"keyword"
                                                }
                                               
                                            }
                                            
                                        }
                                    }
                              }
                              
                    }
                },                
                  
                /////////////////COLLECTION 2

                            

                          
                           
                                
                                    "manager_head_of_collection":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "title":
                                            {
                                                "type": "keyword"
                                            },
                                            "name":
                                            {
                                                "type": "keyword"
                                            },
                                            "phone":
                                            {
                                                "type": "keyword"
                                            },
                                            "email":
                                            {
                                                "type": "keyword"
                                            },
                                            "position":
                                            {
                                                "type": "text"
                                            }
                                            ,
                                            "research_fields":
                                            {
                                                "type": "text"
                                            }
                                        }
                                    }
                               
                               
                           ,
                           "description_fields":
                           {
                                "type":"nested",
                                "properties":
                                {
                                    "outstanding_collection_features":{
                                        "type": "text"
                                    },
                                   "file_info":
                                   {
                                       "type":"text"
                                   },
                                   "specimens_count":
                                   {
                                        "type":"integer"
                                   },
                                    "primary_types_count":
                                   {
                                        "type":"integer"
                                   },
                                    "other_size_indicators":
                                   {
                                        "type":"text"
                                   },
                                   "genetic_repository":
                                   {
                                        "type":"text"
                                   },
                                   "genetic_repository_link":
                                   {
                                        "type":"text"
                                   },
                                   "pc_registered_cards":
                                   {
                                        "type":"text"
                                   },
                                   "pc_recorded_cards_in_database":
                                   {
                                        "type":"text"
                                   },
                                   "ongoing_loans_parcels_specimens_by_year":
                                   {
                                        "type":"text"
                                   },
                                   "accession_specimens":
                                   {
                                        "type":"text"
                                   },
                                   "scientific_visitors_by_year":
                                   {
                                        "type":"text"
                                   },
                                   "visiting_days_by_year":
                                   {
                                        "type":"text"
                                   },
                                   "virtual_access_by_year":
                                   {
                                        "type":"text"
                                   },
                                   "collection_statistics":
                                    {
                                        "type":"text"
                                    }
                                }
                           },
                           "collection_portal_fields":
                           {
                                "type":"nested",
                                "properties":
                                {
                                    "collection_page":
                                    {
                                        "type":"text"
                                    },
                                     "collection_page_url":
                                    {
                                        "type":"keyword"
                                    },
                                    "library":
                                    {
                                        "type":"text"
                                    },
                                    "library_url":
                                    {
                                        "type":"keyword"
                                    },
                                    "archives":
                                    {
                                        "type":"text"
                                    },
                                    "archives_url":
                                    {
                                        "type":"keyword"
                                    },
                                    "other_heritage":
                                    {
                                        "type":"text"
                                    },
                                    "other_heritage_url":
                                    {
                                        "type":"keyword"
                                    }
                                }                            
                           }
                           
                        
                ,
                ////Organisation
                "organisation":
                {
                    "type":"nested",
                    "properties":
                    {
                        
                                    "name" :{
                                        "type": "text"
                                    },
                                    "description" : {
                                        "type": "text"
                                    }
                                    ,
                                    "type_of_institution" : {
                                        "type": "keyword"
                                        /*
                                        TYPE OF INSTITUTION

                                        Museum
                                        Botanical Garden
                                        University
                                        Research Institute
                                        Other

                                        */
                                    },
                                    "type_of_institution_if_other":
                                    {
                                        "type": "keyword"
                                    },
                                    "legal_status":
                                    {
                                        "type":"keyword"
                                        /*
                                            Public
                                            Private
                                            State
                                            Regional
                                            City
                                            Part of a larger entity/legal body
                                        */
                                    },
                                    "if_part_of_a_larger_body":
                                    {
                                        "type":"text"
                                    }
                                    ,
                                    "address":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "street":
                                            {
                                                "type":"text"
                                            },
                                            "city":
                                            {
                                                "type":"text"
                                            },
                                            "postcode":
                                            {
                                                "type":"text"
                                            }
                                            ,
                                            "country":
                                            {
                                                "type":"text"
                                            }
                                            ,
                                            "phone":
                                            {
                                                "type":"text"
                                            }
                                            ,
                                            "email":
                                            {
                                                "type":"text"
                                            }
                                        }
                                    },
                                    "file_information":
                                    {
                                        "type":"keyword"
                                    }
                                
                            ,

                                        "director_or_legal_representative":
                                        {
                                            "type":"nested",
                                            "properties":
                                            {
                                                "title":
                                                {
                                                    "type": "keyword"
                                                },
                                                "name":
                                                {
                                                    "type": "keyword"
                                                },
                                                "phone":
                                                {
                                                    "type": "keyword"
                                                },
                                                "email":
                                                {
                                                    "type": "keyword"
                                                },
                                                "position":
                                                {
                                                    "type": "text"
                                                }
                                                ,
                                                "research_fields":
                                                {
                                                    "type": "text"
                                                }
                                            }
                                        }
                                        ,
                                        "direction_structure_chart":
                                        {
                                            "type":"text"
                                        },
                                        "direction_structure_chart_url":
                                        {
                                            "type":"keyword"
                                        },
                                        "direction_structure_chart_file":
                                        {
                                            "type":"keyword"
                                        },
                                        "direction_governing_and_executive_bodies":
                                        {
                                            "type":"text"
                                        }
                                    
                                    
                            ,
                            "staff_fields":
                            {
                                "type":"nested",
                                "properties":
                                {
                                    "staff_number":
                                    {
                                        "type":"text"
                                    },
                                    "staff_number_permanent":
                                    {
                                        "type":"text"
                                    }
                                    ,
                                    "staff_number_non_permanent":
                                    {
                                        "type":"text"
                                    },
                                    "externalized_service_subcontracted_or_concession":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "function":
                                            {
                                                "type":"keyword"
                                            },
                                             "description":
                                            {
                                                "type":"keyword"
                                            }
                                        }
                                    },
                                    "other_information_scientific_staff":
                                    {
                                        "type":"text"
                                    }
                                }
                            },
                            "membership_fields":
                            {
                                "type":"nested",
                                "properties":
                                {
                                    "membership_date":
                                    {
                                        "type":"date"
                                    },
                                    "membership_category":
                                    {
                                        "type":"keyword"
                                        /*
                                        Full member
                                           Associate member
                                        */
                                    },
                                    "official_representative":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "title":
                                            {
                                                "type": "keyword"
                                            },
                                            "name":
                                            {
                                                "type": "keyword"
                                            },
                                            "phone":
                                            {
                                                "type": "keyword"
                                            },
                                            "email":
                                            {
                                                "type": "keyword"
                                            },
                                            "position":
                                            {
                                                "type": "text"
                                            }
                                            ,
                                            "research_fields":
                                            {
                                                "type": "text"
                                            }
                                        }
                                    },
                                   
                                       
                                            "position_in_the_executive_committee_yes_no":
                                            {
                                                "type":"boolean"
                                            },
                                            "position_in_the_executive_committee_yes_no_text":
                                            {
                                                "type":"text"
                                            }
                                    ,
                                    "staff_members_active_in_cetaf":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "cetaf_deputy":
                                            {
                                                "type":"boolean"
                                            },
                                            "title":
                                            {
                                                "type": "keyword"
                                            },
                                            "name":
                                            {
                                                "type": "keyword"
                                            },
                                            "phone":
                                            {
                                                "type": "keyword"
                                            },
                                            "email":
                                            {
                                                "type": "keyword"
                                            },
                                            "position":
                                            {
                                                "type": "text"
                                            }
                                            ,
                                            "research_fields":
                                            {
                                                "type": "text"
                                            }
                                        }
                                    },

                                     "organisation_portal_fields":
                                   {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "collection_page":
                                            {
                                                "type":"text"
                                            },
                                             "collection_page_url":
                                            {
                                                "type":"keyword"
                                            },
                                            "library":
                                            {
                                                "type":"text"
                                            },
                                            "library_url":
                                            {
                                                "type":"keyword"
                                            },
                                            "archives":
                                            {
                                                "type":"text"
                                            },
                                            "archives_url":
                                            {
                                                "type":"keyword"
                                            },
                                            "other_heritage":
                                            {
                                                "type":"text"
                                            },
                                            "other_heritage_url":
                                            {
                                                "type":"keyword"
                                            }
                                        }                            
                                   }
                                    
                                }
                            }
                    }
                },
                //facility
                "facility":
                {
                    "type":"nested",
                    "properties":{
                            
                                    "name" :{
                                        "type": "text"
                                    },
                                    "description" : {
                                        "type": "text"
                                    }    
                                    
                                
                            ,
                            "list_of_laboratories":
                            {
                                "type":"text"
                            },
                            "list_of_facilities_":
                            {
                                "type":"text"
                            },
                             "other_scientific_facilities":
                            {
                                "type":"text"
                            },
                            "available_tools":
                            {
                                "type":"text"
                            },
                           "available_protocols":
                            {
                                "type":"text"
                            }                           
                           ,
                             "exhibitions":
                            {
                                "type":"text"
                            }
                    
                    }
                },
                /// COMMUNICATION
                "public_relations_and_communication":
                {
                    "type":"nested",
                    "properties":
                    {
                        
                                    "name" :{
                                        "type": "text"
                                    },
                                    "description" : {
                                        "type": "text"
                                    }    
                                    
                                
                            ,
                            "identification_fields":
                            {
                                "type":"nested",
                                "properties":
                                {
                                    "contact_person":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "contact_type":
                                            {
                                                "type": "keyword"
                                                /*person institution*/
                                            },
                                            "title":
                                            {
                                                "type": "keyword"
                                            },
                                            "name":
                                            {
                                                "type": "keyword"
                                            },
                                            "phone":
                                            {
                                                "type": "keyword"
                                            },
                                            "email":
                                            {
                                                "type": "keyword"
                                            }                                            
                                        }
                                    },
                                    "outreach_and_communication_activities":
                                    {
                                        "type":"text"
                                    }
                                }
                            },
                            "visitors_fields":
                            {
                                "type":"nested",
                                "properties":
                                {
                                    "visitors":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "object":
                                            {
                                                "type":"keyword"
                                            },
                                            "year":
                                            {
                                                "type":"integer"
                                            }
                                            ,
                                            "visitors":
                                            {
                                                "type":"integer"
                                            },
                                            "visits_text":
                                            {
                                                "type":"text"
                                            
                                            }
                                        }
                                    }
                                }
                                
                            },
                            "communication_tools":
                            {
                                "type":"nested",
                                "properties":
                                {
                                    "category":
                                    {
                                                "type":"keyword"
                                            
                                    },
                                    "media_name":
                                    {
                                                "type":"text"
                                            
                                    },
                                    "title":
                                    {
                                                "type":"text"
                                            
                                    },
                                    
                                    "link":
                                    {
                                                "type":"keyword"
                                            
                                    }
                                }
                            }                   
                    }
                },
                //EDUCATION
                "education":
                {
                    "type":"nested",
                    "properties":
                    {
                        "training":
                        {
                            "type":"nested",
                            "properties":
                            {
                                "training_type":
                                {
                                    "type":"keyword"
                                    /*
                                        academic
                                        non_academic
                                        other
                                    */
                                },
                                "one_line_or_presential":
                                {
                                    "type":"keyword"
                                }
                                ,
                                "url":
                                {
                                    "type":"keyword"
                                }
                            }
                        }
                    ,
                     "contact_person":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "contact_type":
                                            {
                                                "type": "keyword"
                                                /*person institution*/
                                            },
                                            "title":
                                            {
                                                "type": "keyword"
                                            },
                                            "name":
                                            {
                                                "type": "keyword"
                                            },
                                            "phone":
                                            {
                                                "type": "keyword"
                                            },
                                            "email":
                                            {
                                                "type": "keyword"
                                            }                                            
                                        }
                                    },
                                    "general_description":
                                    {
                                         "type": "text"
                                    }
                           }
                }
            }
      
    }
}
'
