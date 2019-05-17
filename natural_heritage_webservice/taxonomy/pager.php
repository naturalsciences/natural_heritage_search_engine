<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

    class HTMLPager
    {
        protected $data_bag;
        protected $page_size;
        protected $nb_pages;
        protected $page_path;
        protected $headers;
        
        public function __construct($p_data_bag, $p_page_size, $p_page_path, $p_headers)
        {
            $this->data_bag=$p_data_bag;
            $this->page_size=$p_page_size;
            $this->nb_pages= ceil(count($this->data_bag)/$this->page_size);
            $this->page_path = $p_page_path;
			
            $this->headers = $p_headers;
        }
        
        public function getNbPages()
        {
            return $this->nb_pages;
        }
        
        public function getPagerHTML($p_ref_page)
        {
           
            $current=1;
            $returned="";
            $returned.="<table><tr>";
            while($current<=$this->nb_pages)
            {
				if($current==$p_ref_page)
				{					
					$returned.="<td><a href='".$this->page_path.$current."'><b>".$current."</b></a></td>";
				}
				else
				{
					$returned.="<td><a href='".$this->page_path.$current."'>".$current."</a></td>";
                }
				if($current<10||($current>$p_ref_page-15&&$current+10<$p_ref_page+15))
                {
                        $current+=1;
                }
                else
                {
                     $current+=10;
                }
                
            }
            
            $returned.="<td><a href='".$this->page_path.$this->getNbPages()."'>Last</a></td>";
           
            $returned.="</tr></table>";
            return $returned;
        
        }
        
        public function get_page($p_page)
        {
            $returned=Array();
            if(array_key_exists("results", $_SESSION[session_id()]))
            {
                $result_bag= $_SESSION[session_id()]["results"];
                $returned=array_slice($result_bag, ($p_page-1)* $this->page_size, $this->page_size);
                //print_r($tmp);
            }
            return $returned;
        }
        
        //public function getColorCodeRGB($match, $match_color)
        public function getColorCodeRGB($row)
        {
            /*$returned="background-color: ".$match_color;
                           
            if(strpos($match,"synonymy")!==FALSE)
            {
                $returned.=";font-style: italic";
            }
           */
		   if(array_key_exists('background_style', $row)&&array_key_exists('rgb_match_type', $row))
		   {
			   if(strlen(trim($row['background_style']))>0)
			   {
					$returned="background-color: ".$row['rgb_match_type'].";".$row['background_style'];
			   }
			   else
			   {
					$returned="background-color: ".$row['rgb_match_type'];
			   }
		   }
		   else
		   {
			   $returned="";
			   
		   }
            return $returned;
            
        }
        
		
		public function get_statisticsHTML($p_statistics_html)
        {
			$returned="";            
            $returned.="<table>";
            $returned.="<th>Match type</th><th>Count</th>";
            foreach($p_statistics_html as $key=>$row)
			{
				$count=$row["count"];
				$style=$this->getColorCodeRGB($row);
				$returned.="<tr style='".$style."'><td>".$key."</td><td>".$count."</td></tr>";
			}
            $returned.="</table>";
            
            return $returned;
		}
		
        public function get_pageHTML($p_page)
        {
            $returned="";
            $array_data=$this->get_page($p_page);
            $returned.="<table>";
            $returned.="<tr>";
            /*if(is_array($this->headers))
            {   
                if(count($this->headers)>0)
                {
                    
                    foreach($this->headers as $cell)
                    {
                       // $returned.="<th>".$cell."</th>";
                    }
                    
                }
            }*/
            if(is_array($array_data))
            {   
                if(count($array_data)>0)
                {
                    
                    foreach($array_data[0]["parsed_data"] as $key=>$cell)
                    {
                        $returned.="<th>".$key."</th>";
                    }
                    
                }
            }
            $returned.="</tr>";
            foreach($array_data as $row)
            {
                
               
                $originalData=$row['src_data'];
                $parserData=$row['parsed_data'];
                $style=$this->getColorCodeRGB($parserData)  ;
				
                $returned.="<tr style='".$style."'>";
                if(is_array($originalData))
                {
                    foreach($originalData as $cell)
                    {
                        if(isset($cell))
                        {
							$returned.="<td><div style='".$style."'>".$cell."</div></td>";
                        }
						else
						{
							$returned.="<td><div style='".$style."'/></td>";
						}
							
                    }
                }
                
                if(is_array($parserData))
                {
					
                    foreach($parserData as $cell)
                    {
                        if(isset($cell))
                        {
                           $returned.="<td><div style='".$style."'>".$cell."</div></td>";
                        }
						else
						{
							$returned.="<td><div style='".$style."'/></td>";
						}
                     }
                 }
                
                $returned.="</tr>";
            }
            $returned.="</table>";
            
            return $returned;
        }
        

        
    }
    
?>