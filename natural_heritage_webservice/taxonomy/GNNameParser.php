<?php

	class GNNameParser
	{
		
		protected $url_service="http://parser.globalnames.org/api?q=";
		protected $scientific_name;
		protected $json;
		protected $flag = FALSE;
		
		public function __construct($p_scientific_name)
		{
			$this->scientific_name=$p_scientific_name;
			$this->parse();
		}
		
		protected function parse()
		{
			$url = $this->url_service.urlencode($this->scientific_name);
			/*$ch = curl_init();

			// Set the URL
			curl_setopt($ch, CURLOPT_URL, $url);

			// Set to return a string
			curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);

			// Set the timeout
			curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);

			// Execute the API call
			$feed = curl_exec($ch);
			$tmp=json_decode($feed, true);
			if(json_last_error()==JSON_ERROR_NONE)
			{
				$this->flag=true;
				$this->json=$tmp;
			}
			// Close the CURL object
			curl_close($ch);*/
            $tmp=file_get_contents($url);
            $tmp=json_decode($tmp, true);
            if(json_last_error()==JSON_ERROR_NONE)
			{
				$this->flag=true;
				$this->json=$tmp;
			}
			
		}
		
		public function getCanonicalName()
		{
			$returned="";
			if($this->flag)
			{
				$returned=$this->json["namesJson"][0]["canonical_name"]["value"];
			}
			return $returned;
		}
	}
?>