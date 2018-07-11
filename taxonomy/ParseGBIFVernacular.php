<?php
//ini_set('display_errors', 1);
//ini_set('display_startup_errors', 1);
//error_reporting(E_ERROR);

	class ParseGBIFJSONVernacular
	{
		protected $json_doc;
		protected $sc_name;
        protected $url_key="http://api.gbif.org/v1/species/";
        protected $searched_taxa;
		protected $language_array;

		
		public function  __construct($p_json_doc,$p_searched_taxa, $p_language_array)
		{
            $this->json_doc = json_decode($p_json_doc);
            $this->searched_taxa = str_replace('&', '&amp;', $p_searched_taxa); 
			$this->language_array = $p_language_array;
			
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
            $row['gbif_vernacular_match_type']=str_ireplace("FUZZY", "MISSPELLING",$row['gbif_vernacular_match_type']);
            $p_matching_type=$row['gbif_vernacular_match_type'];
            $p_name_status=$row['gbif_vernacular_name_status'];
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
        
        public function initGBIFEmpty(&$returned)
		{
			 $returned["gbif_vernacular_name_status"]="";
             $returned["gbif_vernacular_match_type"] = "NOT_FOUND_REDO";             	
		    $returned["gbif_vernacular_rank"] = ""; 
			$returned["gbif_vernacular_id"] = "";
			$returned["gbif_vernacular_matched"] = "";
			
			foreach($this->language_array as $lang)
			{
				
				$returned["gbif_vernacular_name_".$lang] = Array();
			}
			
			$returned["gbif_vernacular_url"]="";
			
		}
		
        public function returnResult()
		{
			$returned = Array();
            //print_r($this->json_doc);
			$this->initGBIFEmpty($returned);
            $returned["gbif_vernacular_match_type"] = $this->get_info("matchType");
            
            
            if(strtolower($returned["gbif_vernacular_match_type"])=="none")
            {
                if(property_exists( $this->json_doc, "alternatives"))
                {
                    $alt=$this->json_doc->alternatives;
                    if(is_array($alt))
                    {                        
                        
                        $this->json_doc=$this->json_doc->alternatives[0];
                        $returned["gbif_vernacular_match_type"] = $this->get_info("matchType")." (ALTERNATIVE)";
                    }
                }
            }
			
            $returned["gbif_vernacular_name_status"] = strtolower($this->get_info("status"));
            $returned["gbif_vernacular_rank"] = strtolower($this->get_info("rank"));
            $returned["gbif_vernacular_id"] = $this->get_info("usageKey");            
			
			$returned["gbif_vernacular_matched"] = $this->get_info("scientificName");
			
            if(is_numeric($returned["gbif_vernacular_id"]))
            {
              
				
				$url_vernacular="";
                if(property_exists( $this->json_doc, "acceptedUsageKey"))
                {
                    $url_vernacular=$this->url_key.$this->json_doc->acceptedUsageKey;
                }    
				elseif(property_exists( $this->json_doc, "usageKey"))
				{
					$url_vernacular=$this->url_key.$this->json_doc->usageKey;
				}
				if(strlen($url_vernacular)>0)
				{
					$url_vernacular=$url_vernacular."/vernacularNames?limit=500";
					$tmp=file_get_contents($url_vernacular);
                    
					if($tmp)
					{
						$tmp=json_decode($tmp);
						if(property_exists( $tmp, "results"))
						{
							$res=$tmp->results;
							if(is_array($res))
							{                        
								foreach($res as $candidate)
								{
									$this->json_doc=$candidate;
									if(property_exists( $this->json_doc, "language"))
									{
										if(in_array($this->json_doc->language, $this->language_array))
										{
											if(count(preg_grep("/". $this->json_doc->vernacularName."/i",$returned["gbif_vernacular_name_".$this->json_doc->language]))==0)
											{
												$returned["gbif_vernacular_name_".$this->json_doc->language][]= $this->json_doc->vernacularName;
											}
										}
									} 
								}
							}
						}
					}
                 }
				 
				 foreach($this->language_array as $lang)
				{
					
					$returned["gbif_vernacular_name_".$lang] = implode("|",$returned["gbif_vernacular_name_".$lang]);
				}
				 $returned["gbif_vernacular_url"]=$url_vernacular;
                 
                
                
            }
            
            return $returned;
           
        }
		
		
		
	}

?>