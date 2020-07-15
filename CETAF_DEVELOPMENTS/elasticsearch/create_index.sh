curl -X PUT "localhost:9200/cetaf_passport?pretty" -H 'Content-Type: application/json' -d'
{

    "mappings": {
      "dynamic": "strict",
      "properties": {
        "cetaf_institution": {
          "type": "nested",
          "properties": {
            "annual_report_fields": {
              "type": "text"
            },
            "annual_report_fields_url": {
              "type": "keyword"
            },
            "dashboard": {
              "type": "text"
            },
            "dashboard_url": {
              "type": "keyword"
            },
            "institution_description": {
              "type": "text"
            },
            "finances": {
              "type": "nested",
              "properties": {
                "funding_sources_external_euros": {
                  "type": "text"
                },
                "funding_sources_internal_euros": {
                  "type": "text"
                },
                "general_description": {
                  "type": "text"
                },
                "operating_budget_euros": {
                  "type": "integer"
                },
                "other_informations_operating_budget": {
                  "type": "text"
                }
              }
            },
            "identification_fields": {
              "type": "nested",
              "properties": {
                "country_en": {
                  "type": "keyword"
                },
                "country_iso3166": {
                  "type": "keyword"
                },
                "grid_id": {
                  "type": "keyword"
                },
                "grscicoll_code": {
                  "type": "keyword"
                },
                "original_name": {
                  "type": "nested",
                  "properties": {
                    "iso639": {
                      "type": "keyword"
                    },
                    "lang": {
                      "type": "keyword"
                    },
                    "translated_name": {
                      "type": "text"
                    }
                  }
                },
                "unique_acronym": {
                  "type": "keyword"
                },
                "wikidata_id": {
                  "type": "keyword"
                }
              }
            },
            "interest_involvement_cetaf": {
              "type": "nested",
              "properties": {
                "current_topics_of_interest": {
                  "type": "text"
                },
                "future_topics_of_interest": {
                  "type": "text"
                },
                "general_description": {
                  "type": "text"
                }
              }
            },
            "institution_links": {
              "type": "nested",
              "properties": {
                "institution_link_type": {
                  "type": "keyword"
                },
                "institution_url": {
                  "type": "keyword"
                }
              }
            },
            "main_areas_of_taxonomic_expertise": {
              "type": "text"
            },
            "institution_name": {
              "type": "text"
            },
            "research": {
              "type": "nested",
              "properties": {
                "general_description": {
                  "type": "text"
                },
                "research_fields": {
                  "type": "text"
                },
                "research_programs": {
                  "type": "nested",
                  "properties": {
                    "contribution_description": {
                      "type": "text"
                    },
                    "research_links": {
                      "type": "nested",
                      "properties": {
                        "research_link_description": {
                          "type": "keyword"
                        },
                        "research_url": {
                          "type": "keyword"
                        }
                      }
                    },
                    "partner_institutions": {
                      "type": "keyword"
                    },
                    "program_name": {
                      "type": "keyword"
                    },
                    "workpackage_name": {
                      "type": "keyword"
                    }
                  }
                }
              }
            }
          }
        },
        "collection_portal_fields": {
          "type": "nested",
          "properties": {
            "archives": {
              "type": "text"
            },
            "archives_url": {
              "type": "keyword"
            },
            "collection_page": {
              "type": "text"
            },
            "collection_page_url": {
              "type": "keyword"
            },
            "library": {
              "type": "text"
            },
            "library_url": {
              "type": "keyword"
            },
            "other_heritage": {
              "type": "text"
            },
            "other_heritage_url": {
              "type": "keyword"
            }
          }
        },
        "description_fields": {
          "type": "nested",
          "properties": {
            "accession_specimens": {
              "type": "text"
            },
            "collection_statistics": {
              "type": "text"
            },
            "file_info": {
              "type": "text"
            },
            "genetic_repository": {
              "type": "text"
            },
            "genetic_repository_link": {
              "type": "text"
            },
            "ongoing_loans_parcels_specimens_by_year": {
              "type": "text"
            },
            "other_size_indicators": {
              "type": "text"
            },
            "outstanding_collection_features": {
              "type": "text"
            },
            "pc_recorded_cards_in_database": {
              "type": "text"
            },
            "pc_registered_cards": {
              "type": "text"
            },
            "primary_types_count": {
              "type": "integer"
            },
            "scientific_visitors_by_year": {
              "type": "text"
            },
            "specimens_count": {
              "type": "integer"
            },
            "virtual_access_by_year": {
              "type": "text"
            },
            "visiting_days_by_year": {
              "type": "text"
            }
          }
        },
        "education": {
          "type": "nested",
          "properties": {
            "contact_person": {
              "type": "nested",
              "properties": {
                "edu_contact_type": {
                  "type": "keyword"
                },
                "edu_email": {
                  "type": "keyword"
                },
                "edu_name": {
                  "type": "keyword"
                },
                "edu_phone": {
                  "type": "keyword"
                },
                "edu_title": {
                  "type": "keyword"
                }
              }
            },
            "education_general_description": {
              "type": "text"
            },
            "training": {
              "type": "nested",
              "properties": {
                "training_online_or_presential": {
                  "type": "keyword"
                },
                "training_type": {
                  "type": "keyword"
                },
                "training_url": {
                  "type": "keyword"
                }
              }
            }
          }
        },
        "facility": {
          "type": "nested",
          "properties": {
            "available_protocols": {
              "type": "text"
            },
            "available_tools": {
              "type": "text"
            },
            "facility_description": {
              "type": "text"
            },
            "exhibitions": {
              "type": "text"
            },
            "list_of_facilities_": {
              "type": "text"
            },
            "list_of_laboratories": {
              "type": "text"
            },
            "facility_name": {
              "type": "text"
            },
            "other_scientific_facilities": {
              "type": "text"
            }
          }
        },
        "main_type": {
          "type": "keyword"
        },
        "manager_head_of_collection": {
          "type": "nested",
          "properties": {
            "manager_email": {
              "type": "keyword"
            },
            "manager_name": {
              "type": "keyword"
            },
            "manager_phone": {
              "type": "keyword"
            },
            "manager_position": {
              "type": "text"
            },
            "manager_research_fields": {
              "type": "text"
            },
            "manager_title": {
              "type": "keyword"
            }
          }
        },
        "natural_history_collection": {
          "type": "nested",
          "properties": {
            "abstract": {
              "type": "text"
            },
            "acquisition_source": {
              "type": "keyword"
            },
            "administration_field": {
              "type": "nested",
              "properties": {
                "contact_person": {
                  "type": "nested",
                  "properties": {
                    "adm_contact_type": {
                      "type": "keyword"
                    },
                    "adm_email": {
                      "type": "keyword"
                    },
                    "adm_name": {
                      "type": "keyword"
                    },
                    "adm_phone": {
                      "type": "keyword"
                    },
                    "adm_title": {
                      "type": "keyword"
                    }
                  }
                },
                "legal_property": {
                  "type": "text"
                },
                "status": {
                  "type": "keyword"
                }
              }
            },
            "codes": {
              "type": "text"
            },
            "collection_staff": {
              "type": "nested",
              "properties": {
                "staff_collection_role": {
                  "type": "keyword"
                },
                "staff_curatorial_role": {
                  "type": "keyword"
                },
                "staff_degree_msc_discipline": {
                  "type": "keyword"
                },
                "staff_degree_msc_title": {
                  "type": "keyword"
                },
                "staff_description": {
                  "type": "text"
                },
                "staff_expertise_description": {
                  "type": "text"
                },
                "staff_expertise_domain": {
                  "type": "keyword"
                },
                "staff_expertise_geography": {
                  "type": "keyword"
                },
                "staff_first_name": {
                  "type": "text"
                },
                "staff_full_time_equivalent_pc": {
                  "type": "keyword"
                },
                "staff_identifiers": {
                  "type": "nested",
                  "properties": {
                    "system": {
                      "type": "keyword"
                    },
                    "value": {
                      "type": "keyword"
                    }
                  }
                },
                "staff_last_name": {
                  "type": "text"
                },
                "staff_link": {
                  "type": "keyword"
                },
                "staff_phd_msc_discipline": {
                  "type": "keyword"
                },
                "phd_msc_title": {
                  "type": "keyword"
                },
                "staff_status": {
                  "type": "keyword"
                },
                "staff_title": {
                  "type": "keyword"
                }
              }
            },
            "coverage_fields": {
              "type": "nested",
              "properties": {
                "collecting_period_text": {
                  "type": "text"
                },
                "countries_and_areas": {
                  "type": "nested",
                  "properties": {
                    "area_type": {
                      "type": "keyword"
                    },
                    "area_identifier": {
                      "type": "nested",
                      "properties": {
                        "area_identifier_system": {
                          "type": "keyword"
                        },
                        "area_identifier_value": {
                          "type": "keyword"
                        }
                      }
                    },
                    "area_name": {
                      "type": "text"
                    }
                  }
                },
                "functional_group": {
                  "type": "text"
                },
                "geographical_coverage_bbox": {
                  "type": "geo_shape"
                },
                "geographical_coverage_coverage_text": {
                  "type": "text"
                },
                "geographical_coverage_link": {
                  "type": "keyword"
                },
                "habitat": {
                  "type": "nested",
                  "properties": {
                    "habitat_type": {
                      "type": "keyword"
                    },
                    "pc": {
                      "type": "integer"
                    },
                    "texte": {
                      "type": "keyword"
                    }
                  }
                },
                "stratigraphical_coverage_text": {
                  "type": "text"
                },
                "stratigraphical_subdivision": {
                  "type": "keyword"
                },
                "stratigraphy_link": {
                  "type": "keyword"
                },
                "taxonomic_coverage_main_category": {
                  "type": "text"
                },
				
                "taxonomic_coverage_sub_category": {
                  "type": "text"
                },
                "temporal_scope": {
                  "type": "date_range",
                  "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||yyyy"
                }
              }
            },
            "collection_description": {
              "type": "text"
            },
            "description_fields": {
              "type": "nested",
              "properties": {
                "other_size_indicators": {
                  "type": "text"
                },
                "owc_size_evaluation": {
                  "type": "integer"
                }
				,
                "mids_level": {
                  "type": "integer"
                },
                "primary_types_count": {
                  "type": "integer"
                },
                "specimens_count": {
                  "type": "integer"
                },
                "units_count": {
                  "type": "integer"
                }
              }
            },
            "digitisation_fields": {
              "type": "nested",
              "properties": {
                "digitisation_list_texts": {
                  "type": "text"
                },
                "digitisation_list_url": {
                  "type": "keyword"
                },
                "digitisation_strategy": {
                  "type": "text"
                },
                "imaging": {
                  "type": "nested",
                  "properties": {
                    "calibration": {
                      "type": "keyword"
                    },
                    "setup_description": {
                      "type": "text"
                    },
                    "target": {
                      "type": "keyword"
                    },
                    "technique": {
                      "type": "keyword"
                    },
                    "varia": {
                      "type": "text"
                    },
                    "what": {
                      "type": "keyword"
                    },
                    "when": {
                      "type": "date_range",
                      "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd"
                    },
                    "where": {
                      "type": "keyword"
                    },
                    "who": {
                      "type": "keyword"
                    }
                  }
                },
                "proportion_digitised": {
                  "type": "keyword"
                }
              }
            },
            "identification_fields": {
              "type": "nested",
              "properties": {
                "identifier": {
                  "type": "keyword"
                },
                "system": {
                  "type": "keyword"
                }
              }
            },
            "collection_name": {
              "type": "text"
            },
            "original_collectors": {
              "type": "nested",
              "properties": {
                "full_name": {
                  "type": "text"
                },
                "identifier": {
                  "type": "nested",
                  "properties": {
                    "system": {
                      "type": "keyword"
                    },
                    "value": {
                      "type": "keyword"
                    }
                  }
                }
              }
            },
            "storage_fields": {
              "type": "nested",
              "properties": {
                "conservation_container": {
                  "type": "keyword"
                },
                "conservation_container_material": {
                  "type": "keyword"
                },
                "conservation_fluid": {
                  "type": "keyword"
                },
                "conservation_temperature": {
                  "type": "keyword"
                },
                "conservation_text": {
                  "type": "text"
                },
                "curation": {
                  "type": "text"
                },
                "label_information": {
                  "type": "text"
                },
                "label_media": {
                  "type": "keyword"
                },
                "label_system": {
                  "type": "keyword"
                },
                "label_system_if_other": {
                  "type": "keyword"
                },
                "preparation_crosswalk_description_standard": {
                  "type": "keyword"
                },
                "preparation_treatment": {
                  "type": "keyword"
                },
                "preparation_treatment_protocol": {
                  "type": "text"
                }
              }
            },
            "valorisation": {
              "type": "nested",
              "properties": {
                "dataset_citation": {
                  "type": "text"
                },
                "dataset_role": {
                  "type": "keyword"
                },
                "valorisation_description": {
                  "type": "text"
                },
                "valorisation_identification_fields": {
                  "type": "nested",
                  "properties": {
                    "identifier": {
                      "type": "keyword"
                    },
                    "system": {
                      "type": "keyword"
                    }
                  }
                },
                "valorisation_licence": {
                  "type": "keyword"
                },
                "valorisation_licence_holder": {
                  "type": "text"
                },
                "valorisation_title": {
                  "type": "text"
                },
                "valorisation_type": {
                  "type": "keyword"
                },
                "valorisation_url": {
                  "type": "keyword"
                }
              }
            }
          }
        },
        "organisation": {
          "type": "nested",
          "properties": {
            "address": {
              "type": "nested",
              "properties": {
                "city": {
                  "type": "text"
                },
                "country": {
                  "type": "text"
                },
                "email": {
                  "type": "text"
                },
                "phone": {
                  "type": "text"
                },
                "postcode": {
                  "type": "text"
                },
                "street": {
                  "type": "text"
                }
              }
            },
            "description": {
              "type": "text"
            },
            "direction_governing_and_executive_bodies": {
              "type": "text"
            },
            "direction_structure_chart": {
              "type": "text"
            },
            "direction_structure_chart_file": {
              "type": "keyword"
            },
            "direction_structure_chart_url": {
              "type": "keyword"
            },
            "director_or_legal_representative": {
              "type": "nested",
              "properties": {
                "dir_rep_email": {
                  "type": "keyword"
                },
                "dir_rep_name": {
                  "type": "keyword"
                },
                "dir_rep_phone": {
                  "type": "keyword"
                },
                "dir_rep_position": {
                  "type": "text"
                },
                "dir_rep_research_fields": {
                  "type": "text"
                },
                "dir_rep_title": {
                  "type": "keyword"
                }
              }
            },
            "file_information": {
              "type": "keyword"
            },
            "if_part_of_a_larger_body": {
              "type": "text"
            },
            "legal_status": {
              "type": "keyword"
            },
            "membership_fields": {
              "type": "nested",
              "properties": {
                "membership_category": {
                  "type": "keyword"
                },
                "membership_date": {
                  "type": "date"
                },
                "official_representative": {
                  "type": "nested",
                  "properties": {
                    "member_rep_email": {
                      "type": "keyword"
                    },
                    "member_rep_name": {
                      "type": "keyword"
                    },
                    "member_rep_phone": {
                      "type": "keyword"
                    },
                    "member_rep_position": {
                      "type": "text"
                    },
                    "member_rep_research_fields": {
                      "type": "text"
                    },
                    "member_rep_title": {
                      "type": "keyword"
                    }
                  }
                },
                "organisation_portal_fields": {
                  "type": "nested",
                  "properties": {
                    "archives": {
                      "type": "text"
                    },
                    "archives_url": {
                      "type": "keyword"
                    },
                    "collection_page": {
                      "type": "text"
                    },
                    "collection_page_url": {
                      "type": "keyword"
                    },
                    "library": {
                      "type": "text"
                    },
                    "library_url": {
                      "type": "keyword"
                    },
                    "other_heritage": {
                      "type": "text"
                    },
                    "other_heritage_url": {
                      "type": "keyword"
                    }
                  }
                },
                "position_in_the_executive_committee_yes_no": {
                  "type": "boolean"
                },
                "position_in_the_executive_committee_yes_no_text": {
                  "type": "text"
                },
                "staff_members_active_in_cetaf": {
                  "type": "nested",
                  "properties": {
                    "cetaf_deputy": {
                      "type": "boolean"
                    },
                    "cetaf_staff_email": {
                      "type": "keyword"
                    },
                    "cetaf_staff_name": {
                      "type": "keyword"
                    },
                    "cetaf_staff_phone": {
                      "type": "keyword"
                    },
                    "cetaf_staff_position": {
                      "type": "text"
                    },
                    "cetaf_staff_research_fields": {
                      "type": "text"
                    },
                    "cetaf_staff_title": {
                      "type": "keyword"
                    }
                  }
                }
              }
            },
            "organisation_name": {
              "type": "text"
            },
            "staff_fields": {
              "type": "nested",
              "properties": {
                "externalized_service_subcontracted_or_concession": {
                  "type": "nested",
                  "properties": {
                    "description": {
                      "type": "keyword"
                    },
                    "function": {
                      "type": "keyword"
                    }
                  }
                },
                "other_information_scientific_staff": {
                  "type": "text"
                },
                "staff_number": {
                  "type": "text"
                },
                "staff_number_non_permanent": {
                  "type": "text"
                },
                "staff_number_permanent": {
                  "type": "text"
                }
              }
            },
            "type_of_institution": {
              "type": "keyword"
            },
            "type_of_institution_if_other": {
              "type": "keyword"
            }
          }
        },
        "parent_relationship": {
          "type": "join",
          "eager_global_ordinals": true,
          "relations": {
            "root": "detail",
            "detail": "root"
          }
        },
        "public_relations_and_communication": {
          "type": "nested",
          "properties": {
            "communication_tools": {
              "type": "nested",
              "properties": {
                "comm_tool_category": {
                  "type": "keyword"
                },
                "comm_tool_link": {
                  "type": "keyword"
                },
                "comm_tool_media_name": {
                  "type": "text"
                },
                "comm_tool_title": {
                  "type": "text"
                }
              }
            },
            "comm_description": {
              "type": "text"
            },
            "comm_identification_fields": {
              "type": "nested",
              "properties": {
                "contact_person": {
                  "type": "nested",
                  "properties": {
                    "comm_contact_type": {
                      "type": "keyword"
                    },
                    "comm_email": {
                      "type": "keyword"
                    },
                    "comm_name": {
                      "type": "keyword"
                    },
                    "comm_phone": {
                      "type": "keyword"
                    },
                    "comm_title": {
                      "type": "keyword"
                    }
                  }
                },
                "outreach_and_communication_activities": {
                  "type": "text"
                }
              }
            },
            
            "visitors_fields": {
              "type": "nested",
              "properties": {
                "visitors": {
                  "type": "nested",
                  "properties": {
                    "object": {
                      "type": "keyword"
                    },
                    "visitors": {
                      "type": "integer"
                    },
                    "visits_text": {
                      "type": "text"
                    },
                    "year": {
                      "type": "integer"
                    }
                  }
                }
              }
            }
          }
        },
        "url_id": {
          "type": "text"
        }
		,
        "full_path": {
          "type": "text"
        },
		"parent_institution":{
			"type":"text"
		},
		"list_parent_collections":{
			"type":"text"
		}
      }
    }
  
}
'
