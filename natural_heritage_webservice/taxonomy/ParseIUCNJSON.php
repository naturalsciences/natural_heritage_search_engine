<?php
//ini_set('display_errors', 1);
//ini_set('display_startup_errors', 1);
//error_reporting(E_ERROR);

	class ParseIUCNJSON
	{
		protected $json_doc;
		protected $sc_name;
        protected $url_key="http://apiv3.iucnredlist.org/api/v3/species/";
        protected $url_key_country="https://apiv3.iucnredlist.org/api/v3/species/countries/name/";
        protected $token;
		protected $gbif_status;
		protected $gbif_match_type;
		protected $gbif_name;
		
		public function  __construct($p_token, $p_sc_name)
		{
            $this->token = $p_token;
			$this->sc_name = $p_sc_name;
			         
		}
        
        
		

        public static function initIUCNEmpty(&$returned)
		{
			 $returned["iucn_name"]="";
			 $returned["iucn_category"]="";
             $returned["iucn_criteria"]="";
			 $returned["iucn_year"]="";
             $returned["iucn_common_name"]="";
             $returned["iucn_population_trend"]="";
             $returned["iucn_marine_system"]="";
             $returned["iucn_freshwater_system"]="";
             $returned["iucn_terrestrial_system"]="";
             $returned["iucn_countries"]="";
			 $returned["iucn_url"]="";
			 
			
		}
        public function returnResult()
		{
			$returned = Array();
            //print_r($this->json_doc);
			ParseIUCNJSON::initIUCNEmpty($returned);
			if(isset($this->gbif_name))
			{
				if(strpos(strtolower($this->gbif_status), "synonym")!==false||strpos(strtolower($this->gbif_match_type), "exact")===false)
				{
					$this->sc_name=$this->gbif_name;
				}
			}
            $returned["iucn_name"] = $this->sc_name;
            
			$url_iucn=$this->url_key . str_replace(" ", "%20",$this->sc_name). "?token=".$this->token;
            $url_iucn_2= $this->url_key_country . str_replace(" ", "%20",$this->sc_name). "?token=".$this->token;
            $curl = curl_init();
            curl_setopt_array($curl, [
                CURLOPT_RETURNTRANSFER => 1,
                CURLOPT_URL => $url_iucn,
                CURLOPT_USERAGENT => 'Codular Sample cURL Request'
            ]);
            curl_setopt($curl, CURLOPT_HEADER,"Accept: application/json");
            // Send the request & save response to $resp
            $tmp = curl_exec($curl);
            // Close request to clear up some resources
            curl_close($curl);
           
           
            $curl = curl_init();
            curl_setopt_array($curl, [
                CURLOPT_RETURNTRANSFER => 1,
                CURLOPT_URL => $url_iucn_2,
                CURLOPT_USERAGENT => 'Codular Sample cURL Request'
            ]);
            curl_setopt($curl, CURLOPT_HEADER,"Accept: application/json");
            // Send the request & save response to $resp
            $tmp2 = curl_exec($curl);
            
            // Close request to clear up some resources
            curl_close($curl);
            
			if($tmp!==false)
			{
               
				$this->json_doc =json_decode($tmp, true);
                $this->json_countries =json_decode($tmp2, true);
                print_r($this->json_doc);
				if(!is_null($this->json_doc))
				{
					  $returned["iucn_category"] = $this->json_doc["result"][0]["category"];
					  $returned["iucn_criteria"] = $this->json_doc["result"][0]["criteria"];
					  $returned["iucn_year"] = $this->json_doc["result"][0]["published_year"];
                      $returned["iucn_common_name"] = $this->json_doc["result"][0]["main_common_name"];
                      $returned["iucn_population_trend"] =$this->json_doc["result"][0]["population_trend"];
                      $returned["iucn_marine_system"] =$this->json_doc["result"][0]["marine_system"];
                      $returned["iucn_freshwater_system"] =$this->json_doc["result"][0]["freshwater_system"];
                      $returned["iucn_terrestrial_system"] = $this->json_doc["result"][0]["terrestrial_system"];
                      if(!is_null($this->json_countries))
                      {
                       
                        $countries=Array();
                        foreach( $this->json_countries["result"] as $sub_array)
                        {
                           
                           $countries[]="{'iso_code': '".$sub_array["code"]."','distribution_code' : '".$sub_array["distribution_code"]."'}"; 
                        }
                        $returned["iucn_countries"]="[".implode(",", $countries)."]";
					  }
                      $returned["iucn_url"] = $url_iucn;
				}
			}
            
            return $returned;
           
        }
		
		
		
	}

?>