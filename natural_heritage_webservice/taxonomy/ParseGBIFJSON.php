<?php
//ini_set('display_errors', 1);
//ini_set('display_startup_errors', 1);
//error_reporting(E_ERROR);
ini_set('default_socket_timeout', 5);

	class ParseGBIFJSON
	{
		protected $json_doc;
		protected $sc_name;
        protected $url_key="http://api.gbif.org/v1/species/";
        protected $searched_taxa;
		
		public function  __construct($p_json_doc,$p_searched_taxa)
		{
            $this->json_doc = json_decode($p_json_doc);
            $this->searched_taxa = str_replace('&', '&amp;', $p_searched_taxa);            
		}
        
        
        protected function get_info($p_prop, $p_obj=null)
        {
            $returned="";
            if(is_null($p_obj))
            {
                $p_obj =$this->json_doc;
            }
            if(property_exists( $p_obj, $p_prop))
            {
                $returned=$p_obj->$p_prop;
            }
            return $returned;
        }
        public function setRGBCode(&$row)
        {
            $row['gbif_match_type']=str_ireplace("FUZZY", "MISSPELLING",$row['gbif_match_type']);
            $p_matching_type=$row['gbif_match_type'];
            $p_name_status=$row['gbif_name_status'];
            $p_matching_type= preg_replace('/\(.+\)/','',$p_matching_type);
            $rgb="#ffffff";
            $background_style ="";
            $backgroundstyle="";
            switch($p_matching_type)
            {
                case "EXACT":
                    $rgb="#00cc00";
                    break;
                case "EXACT_OTHER_AUTHOR":
                    $rgb="#22ff22";
                    break;
                case "HIGHERRANK":
                    $rgb="#ffbf00";
                    break;
            }
            if(strpos($p_matching_type, "NOT_FOUND")!==FALSE)
            {
                $rgb="#ff0000";
            }
            elseif(strpos($p_matching_type, "MISSPELLING")!==FALSE)
            {
                $rgb="#ffff00";
            }
           if(strpos($p_name_status, "synonym")!==FALSE)
           {
                 $background_style="font-style: italic;  font-weight: bold;";
           }
           $row['background_style']=$background_style;
           $row['rgb_match_type']=$rgb;
        
        }
        
        public static function initGBIFEmpty(&$returned)
		{
			 $returned["gbif_name_status"]="";
             $returned["gbif_match_type"] = "NOT_FOUND_REDO";             	
		    $returned["gbif_rank"] = ""; 
			$returned["gbif_id"] = "";
			$returned["gbif_matched"] = "";
			//Kingdom
			$returned["gbif_kingdom"] = "";
			//Phylum
			$returned["gbif_phylum"] = "";
            //Phylum
			$returned["gbif_class"] = "";
			//Order
			$returned["gbif_order"] = "";
			//Family
			$returned["gbif_family"]= "";
			//Genus
			$returned["gbif_genus"]= "";
			//Species
			$returned["gbif_species"]= "";
			//Subspecies
			$returned["gbif_subspecies"]= "";
			//full name
				
            $returned["gbif_full_name"] = "";					
            $returned["gbif_author"] = "";
            $returned["gbif_source"] = "";
            $returned["gbif_reference"] = "";
            $returned["rgb_match_type"]="#ffffff";
            $returned['background_style']="";
			
			$returned["gbif_url"]="";
			
		}
        public function returnResult()
		{
			$returned = Array();
            //print_r($this->json_doc);
			ParseGBIFJSON::initGBIFEmpty($returned);
            $returned["gbif_match_type"] = $this->get_info("matchType");
            
            
            if(strtolower($returned["gbif_match_type"])=="none")
            {
                if(property_exists( $this->json_doc, "alternatives"))
                {
                    $alt=$this->json_doc->alternatives;
                    if(is_array($alt))
                    {                        
                        
                        $this->json_doc=$this->json_doc->alternatives[0];
                        $returned["gbif_match_type"] = $this->get_info("matchType")." (ALTERNATIVE)";
                    }
                }
            }
			
            $returned["gbif_name_status"] = strtolower($this->get_info("status"));
            $returned["gbif_rank"] = strtolower($this->get_info("rank"));
            $returned["gbif_id"] = $this->get_info("usageKey");            
			
			$returned["gbif_matched"] = $this->get_info("scientificName");
			
            if(is_numeric($returned["gbif_id"]))
            {
              
                            //Kingdom
                $returned["gbif_kingdom"] = $this->get_info("kingdom");
                //Phylum
                $returned["gbif_phylum"] = $this->get_info("phylum");
                //Phylum
                $returned["gbif_class"] = $this->get_info("class");
                //Order
                $returned["gbif_order"] = $this->get_info("order");
                //Family
                $returned["gbif_family"] = $this->get_info("family");
                //Genus
                $returned["gbif_genus"] = $this->get_info("genus");
                //Species
                $returned["gbif_species"] = $this->get_info("species");
                //Subspecies
                if($returned["gbif_rank"]=="subspecies")
                {
                    $returned["gbif_subspecies"] = $this->get_info("scientificName");
                }
                //full name	
				
				$url_details="";
                if(property_exists( $this->json_doc, "acceptedUsageKey"))
                {
                    $url_details=$this->url_key.$this->json_doc->acceptedUsageKey;
                }    
				elseif(property_exists( $this->json_doc, "usageKey"))
				{
					$url_details=$this->url_key.$this->json_doc->usageKey;
				}
				if(strlen($url_details)>0)
				{
					$tmp=file_get_contents($url_details);
                    
					if($tmp)
					{
						$tmp=json_decode($tmp);
						$returned["gbif_full_name"] = $this->get_info("canonicalName",$tmp);	
						$returned["gbif_source"] = $this->get_info("original",$tmp);	
						$returned["gbif_reference"] = $this->get_info("publishedIn", $tmp);	
						$returned["gbif_author"] =  $this->get_info("authorship", $tmp);	
					}
                 }
                 
                
                
            }
			if($returned["gbif_match_type"]=="EXACT"&&(strpos(strtolower($returned["gbif_name_status"]),"synonym")!==FALSE)&&($this->get_info("scientificName") != $this->searched_taxa ))
			{
				$returned["gbif_match_type"]="EXACT_OTHER_AUTHOR";
			}
			elseif($returned["gbif_match_type"]=="EXACT"&&(strpos(strtolower($returned["gbif_name_status"]),"synonym")!==FALSE)&&($this->get_info("scientificName") == $this->searched_taxa ))
			{
				$returned["gbif_match_type"]="EXACT";
			}
            elseif($returned["gbif_match_type"]=="EXACT"&& trim(str_replace($returned["gbif_author"] ,'', $returned["gbif_full_name"] ))." ".trim($returned["gbif_author"]) != $this->searched_taxa )
            {
                        $returned["gbif_match_type"]="EXACT_OTHER_AUTHOR";
            }
            $this->setRGBCode($returned);
            return $returned;
           
        }
		
		
		
	}

?>