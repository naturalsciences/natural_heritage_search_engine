<?php
//ini_set('display_errors', 1);
//ini_set('display_startup_errors', 1);
//error_reporting(E_ERROR);
ini_set('default_socket_timeout', 5);

	class ParseDarwinJSON
	{
		protected $json_doc;
		protected $sc_name;
		protected $complete_sc_name;
        protected $url_key="http://darwin.naturalsciences.be/public.php/search/CheckTaxonHierarchy?canonical=true&taxon-name=";
        protected $compare_gbif;
		protected $gbif_array;
		
		public function  __construct( $p_sc_name, $p_complete_sc_name="", $p_compare_gbif=false, $p_gbif_array=null)
		{
           
			$this->sc_name = $p_sc_name;
			$this->complete_sc_name= $p_complete_sc_name;
			$this->compare_gbif=$p_compare_gbif;
			$this->gbif_array=$p_gbif_array;
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
		

        public static function initDarwinEmpty(&$returned)
		{
			 $returned["darwin_full_name"]="";
			 $returned["darwin_found"]="";
             $returned["darwin_match_type"]="";
			 $returned["darwin_hierarchy"]="";
			 $returned["darwin_hierarchy_matches_gbif"]="";
			 $returned["darwin_url"]="";
			 
			
		}
        public function returnResult()
		{
			$returned = Array();
            //print_r($this->json_doc);
			ParseDarwinJSON::initDarwinEmpty($returned);
			
			$url_darwin= $this->url_key . urlencode($this->sc_name);
			 $tmp=file_get_contents($url_darwin);
			if($tmp!==false)
			{
				$this->json_doc = json_decode($tmp);
				if(!is_null($this->json_doc))
				{
					 $matches=$this->json_doc->matches;
					 $names=Array();
					 $matchType=Array();
					 $darwin_hierarchy=Array();
					if(is_array($matches))
                     {                        
                        $darwin_hierarchy_matches_gbif=false;
                        foreach($matches as $key=>$match)
						{
							$this->json_doc=$match;
							$names[]=$this->get_info("name");
							if(strlen($this->complete_sc_name)>0&&$this->complete_sc_name!=$this->sc_name)								
							{
								if($this->get_info("name")==$this->complete_sc_name)
								{
									$matchType[]="SAME_AUTHOR";
								}
								else
								{
									$matchType[]="OTHER_AUTHOR";
								}
							}
							else
							{
								$matchType[]=$this->get_info("match");
							}
							
							$hierarchy=(array)$this->json_doc->hierarchy;
							
							if(is_array($hierarchy))
							{
								
								$darwin_hierarchy[]=json_encode($hierarchy);
								if($this->compare_gbif)
								{
									if(!$darwin_hierarchy_matches_gbif)
									{
										$tmp_match_gbif=true;
										foreach($hierarchy as $rank=>$name)
										{
											if(array_key_exists("gbif_".$rank,$this->gbif_array))
											{
												if($this->gbif_array["gbif_".$rank]!=$name)
												{
													$tmp_match_gbif=false;
													break;
												}
											}
										}
										 $darwin_hierarchy_matches_gbif=$tmp_match_gbif;
									}
									
								}
							}	
						}
                     }
					  //$returned["darwin_full_name"]="";
					  if($this->get_info("found"))
					  {
						$returned["darwin_found"]="true";
					  }
					  else
					  {
						  $returned["darwin_found"]="false";
					  }
					  $returned["darwin_full_name"]=implode(";",$names);
					  $returned["darwin_match_type"]=implode(";",$matchType);
			          $returned["darwin_hierarchy"]=implode(";",$darwin_hierarchy);
					   $returned["darwin_hierarchy_matches_gbif"]=$darwin_hierarchy_matches_gbif;
					   if($darwin_hierarchy_matches_gbif)
					  {
						$returned["darwin_hierarchy_matches_gbif"]="true";
					  }
					  else
					  {
						  $returned["darwin_hierarchy_matches_gbif"]="false";
					  }
					  $returned["darwin_url"]=$url_darwin;
				}
			}
			
            return $returned;
           
        }
		
		
		
	}

?>