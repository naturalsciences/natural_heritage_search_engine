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
                        "title_fields" :
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
                            }
                        },
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
                        "dashboard_fields":
                        {
                            "type": "nested",
                            "properties":
                            {
                                "dashboard":
                                {
                                    "type": "text"
                                },
                                "dashboard_url":
                                {
                                    "type": "keyword"
                                }
                            }
                        },
                        "annual_report_fields":
                        {
                            "type": "nested",
                            "properties":
                            {
                                "reports_accounts":
                                {
                                    "type": "text"
                                },
                                "reports_accounts_url":
                                {
                                    "type": "keyword"
                                }
                            }
                        },
                        "gbif_field":
                        {
                            "type": "nested",
                            "properties":
                            {
                                "gbif_text":
                                {
                                    "type": "text"
                                },
                                "gbif_link_url":
                                {
                                    "type": "keyword"
                                }
                            }
                        }
                    }
                 },
                  /////////////////COLLECTION 1
                "natural_history_collection":
                {
                    "type":"nested",
                    "properties": 
                    {
                        "title_fields" :
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
                                    "abstract" : {
                                        "type": "text"
                                    }
                                    
                                }
                            },
                            "identification_fields":
                            {
                                        "type": "nested",
                                        "properties":
                                        {
                                            "doi" : {
                                                "type": "keyword"
                                            },
                                            "other_identiers":
                                            {
                                                "type":"nested",
                                                "properties":
                                                {
                                                    "system":
                                                    {
                                                        "type":"keyword"
                                                    },
                                                    "identifier":
                                                    {
                                                        "type":"keyword"
                                                    }
                                                }
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
                                    },
                                    "geographical_coverage":
                                    {
                                         "type":"nested",
                                        "properties":
                                        {
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
                                    }
                                }
                              },
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
                                            "mail":
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
                "collection_group" :
                {
                 
                        "type": "nested",
                        "properties":
                        {
                            "title_fields" :
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
                                }
                            },
                          "identification_fields" :
                           {
                                "type": "nested",
                                "properties":{
                                    "lsid":{
                                        "type": "keyword"
                                    },
                                    "herbarium_index_code": 
                                    {
                                        "type": "keyword"
                                    }
                                }
                           },
                           "manager_fields":
                           {
                                "type":"nested",
                                "properties":
                                {
                                
                                    "head_of_collection":
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
                                            "mail":
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
                           
                        }
                },
                ////Organisation
                "organisation":
                {
                    "type":"nested",
                    "properties":
                    {
                        "title_fields" :
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
                                }
                            },
                            "direction_fields":
                            {       
                                    "type":"nested",
                                    "properties":
                                    {
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
                                                "mail":
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
                                        "structure_chart":
                                        {
                                            "type":"text"
                                        },
                                        "structure_chart_url":
                                        {
                                            "type":"keyword"
                                        },
                                        "structure_chart_file":
                                        {
                                            "type":"keyword"
                                        },
                                        "governing_and_executive_bodies":
                                        {
                                            "type":"text"
                                        }
                                    }
                                    
                            },
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
                                            "mail":
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
                                    "position_in_the_executive_committee":
                                    {
                                        "type":"nested",
                                        "properties":
                                        {
                                            "yes_no":
                                            {
                                                "type":"boolean"
                                            },
                                            "description":
                                            {
                                                "type":"text"
                                            }
                                        }
                                    },
                                    "cetaf_deputy":
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
                                            "mail":
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
                                    "other_staff_members_active_in_cetaf":
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
                                            "mail":
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
                            "title_fields" :
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
                                    
                                }
                            },
                            "list_of_laboratories":
                            {
                                "type":"text"
                            },
                            "list_of_facilities":
                            {
                                "type":"text"
                            },
                             "other_scientific_facilities":
                            {
                                "type":"text"
                            },
                             "exhibitions":
                            {
                                "type":"text"
                            }
                    
                    }
                }
                /// COMMUNICATION
            }
      
    }
}
'
