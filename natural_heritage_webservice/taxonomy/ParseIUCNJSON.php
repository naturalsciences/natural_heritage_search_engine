<?php
//ini_set('display_errors', 1);
//ini_set('display_startup_errors', 1);
//error_reporting(E_ERROR);

	class ParseIUCNJSON
	{
		protected $json_doc;
		protected $sc_name;
        protected $url_key="http://apiv3.iucnredlist.org/api/v3/species/";
        protected $token;
		protected $gbif_status;
		protected $gbif_match_type;
		protected $gbif_name;
		
		public function  __construct($p_token, $p_sc_name, $p_gbif_status=false, $p_gbif_match_type=false, $p_gbif_name=null)
		{
            $this->token = $p_token;
			$this->sc_name = $p_sc_name;
			$this->gbif_status = $p_gbif_status;
			$this->gbif_match_type = $p_gbif_match_type;
			$this->gbif_name = $p_gbif_name;            
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
		

        public static function initGBIFEmpty(&$returned)
		{
			 $returned["iucn_name"]="";
			 $returned["iucn_category"]="";
             $returned["iucn_criteria"]="";
			 $returned["iucn_year"]="";
			 $returned["iucn_url"]="";
			 
			
		}
        public function returnResult()
		{
			$returned = Array();
            //print_r($this->json_doc);
			ParseIUCNJSON::initGBIFEmpty($returned);
			if(isset($this->gbif_name))
			{
				if(strpos(strtolower($this->gbif_status), "synonym")!==false||strpos(strtolower($this->gbif_match_type), "exact")===false)
				{
					$this->sc_name=$this->gbif_name;
				}
			}
            $returned["iucn_name"] = $this->sc_name;
            
			$url_iucn= $this->url_key . $this->sc_name. "?token=".$this->token;
            
            $tmp=file_get_contents($url_iucn);
			if($tmp!==false)
			{
				$this->json_doc = json_decode($tmp);
				if(!is_null($this->json_doc))
				{
					  $returned["iucn_category"] = $this->get_info("category");
					  $returned["iucn_criteria"] = $this->get_info("criteria");
					  $returned["iucn_criteria"] = $this->get_info("published_year");
					  $returned["iucn_url"] = $url_iucn;
				}
			}
            return $returned;
           
        }
		
		
		
	}

?>