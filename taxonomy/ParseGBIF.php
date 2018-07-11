<?php
//ini_set('display_errors', 1);
//ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
	class ParseGBIF
	{
		protected $domDoc;
		protected $xpath;
		protected $loaded;
        protected $searched_taxa;
		
		public function  __construct($p_str, $p_searched_taxa)
		{
            $this->searched_taxa = str_replace('&', '&amp;', $p_searched_taxa);
			$this->domDoc = new DOMDocument();
			
			$this->loaded=false;
            
			
            if(strlen($p_str)>0)
            {
                $p_str= str_replace('&', '&amp;', $p_str);
                
                $this->loaded=$this->domDoc->loadXML($p_str);
                
                if($this->loaded)
                {
                    $this->xpath = new DOMXpath($this->domDoc);
                }
            }
		}
		
		protected function getStrFromNode($p_obj, $p_path)
		{
            $returned= "";
			$node = $this->xpath->query($p_path);
			if($node)
            {
                if($node->length>0)
                {
                    
                    $tmp=$node->item(0);
                    $returned=trim($tmp->nodeValue);
                }
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
				
			$returned["gbif_id"] = "";
				//Kingdom
					$returned["gbif_kingdom"] = "";
				//Phylum
					$returned["gbif_phylum"] = "";
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
                $returned["rgb_match_type"]="#ffffff";
            $returned['background_style']="";
			
			$returned["gbif_url"]="";
			
		}
		
		public function returnResult()
		{
			$returned = Array();
            
			ParseGBIF::initGBIFEmpty($returned);
			
			if($this->loaded)
			{
                //accepted
				//is synonym
				
                $is_synonym = false;
                $path_prefix= "/results/result";
                $returned["gbif_name_status"] = $this->getStrFromNode("/results/result/name_status");
                if($returned["gbif_name_status"]=="synonym")
                {
                    $is_synonym=TRUE;				
                }
                if($is_synonym)
                {
                    $path_prefix= "/results/result/accepted_name";
                }
			
				//match type
					//exact
					//different author
					//fuzzy
					//higher rank
					//none
				$tmpMatch= $this->getStrFromNode("/results/result/matchType");
                if(strlen($tmpMatch)>0)
                {
                    $returned["gbif_match_type"] =$tmpMatch;
				}
				
				
				//gbif id
				$returned["gbif_id"] = $this->getStrFromNode("/results/result/id");
				
				
				//Kingdom
					$returned["gbif_kingdom"] = $this->getStrFromNode($path_prefix.'/classification/taxon[rank/text()="Kingdom"]/name/text()');	
				//Phylum
					$returned["gbif_phylum"] = $this->getStrFromNode($path_prefix.'/classification/taxon[rank/text()="Phylum"]/name/text()');	
				//Order
					$returned["gbif_order"] = $this->getStrFromNode($path_prefix.'/classification/taxon[rank/text()="Order"]/name/text()');
				//Family
					$returned["gbif_family"] = $this->getStrFromNode($path_prefix.'/classification/taxon[rank/text()="Family"]/name/text()');
				//Genus
					$returned["gbif_genus"] = $this->getStrFromNode($path_prefix.'/classification/taxon[rank/text()="Genus"]/name/text()');
				//Species
					$returned["gbif_species"] = $this->getStrFromNode($path_prefix.'/classification/taxon[rank/text()="Species"]/name/text()');
				//Subspecies
					$returned["gbif_subspecies"] = $this->getStrFromNode($path_prefix.'/classification/taxon[rank/text()="Subspecies"]/name/text()');
				//full name
				
					$returned["gbif_full_name"] = $this->getStrFromNode($path_prefix."/name");					
				
					
				
				//Author
					$returned["gbif_author"] = $this->getStrFromNode($path_prefix."/author");

                    if($returned["gbif_match_type"]=="EXACT"&& trim(str_replace($returned["gbif_author"] ,'', $returned["gbif_full_name"] ))." ".trim($returned["gbif_author"]) != $this->searched_taxa )
                    {
                        $returned["gbif_match_type"]="EXACT_OTHER_AUTHOR";
                    }
				

				
				
				//confidence
                
                $this->setRGBCode($returned);
			
			}
            
           
			return $returned;
			
		}
		
	}

?>