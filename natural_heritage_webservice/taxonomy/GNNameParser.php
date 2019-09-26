<?php

	class GNNameParser
	{
		
		protected $scientific_name;
		protected $json;
		protected $flag = FALSE;
        protected $result;
		
		public function __construct($p_scientific_name)
		{
			$this->scientific_name=trim(trim($p_scientific_name,"'"),'"');
			$this->parse();
		}
		
		protected function parse()
		{
            $cmd='gnparser "'.$this->scientific_name.'"';

            $this->result= shell_exec($cmd);
            $this->json=json_decode($this->result, TRUE);
			
			
		}
		
		public function getCanonicalName()
		{
			
            $returned=$this->json["canonicalName"]["simple"];			
           
			return $returned;
		}
	}
?>