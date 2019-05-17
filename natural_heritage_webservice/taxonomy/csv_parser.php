<?php
/*ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ERROR );
*/
require_once("restHelper_curl.php");
require_once("Encoding.php");
use \ForceUTF8\Encoding;

require_once("ParseGBIFJSON.php");
require_once("ParseDarwinJSON.php");
require_once("ParseIUCNJSON.php");
require_once("ParseGBIFVernacular.php");
require_once("GNNameParser.php");
require_once("MyDB.php");

class CSVParser 
{
	
		protected $srcFile;
		protected $delimiter;
		protected $hasHeader;
		protected $nbFields;
		protected $idxDataField;
		protected $idxKingdomField;
        protected $url_webservice_gbif= "http://api.gbif.org/v1/species/match?verbose=true&name=";
        protected $url_webservice_worms= "http://www.marinespecies.org/aphia.php?p=soap&wsdl=1";
		protected $iucn_token= "9bb4facb6d23f48efbf424bb05c0c1ef1cf6f468393bc745d42179ac4aca5fee";
		protected $kingdom_suffix= "";
        protected $holder=Array();
        protected $complete_result=Array();
        protected $headers=Array();
        protected $sources=Array();
		protected $languages = Array();
        protected $runFlag=true;
		protected $deleted=FALSE;
       
        public $mail;
       
        //protected $gearman_client;
	   
		
		public function __construct($p_file, $p_mail, $p_index_data, $p_has_headers, $p_delimiter, $p_index_kingdom, $p_sources, $p_languages=null)
		{
            try
            {
                print("load");
                
  
                //$this->gearman_client = new GearmanClient();
                //$this->gearman_client->addServer("127.0.0.1");
                print("create pdo");
                //
                
                print("pdo created");
                $this->mail = $p_mail;
                $this->srcFile=$p_file;
                $this->idxDataField=$p_index_data-1;
                $this->hasHeader = $p_has_headers;
                $this->delimiter = $p_delimiter;
                if(is_numeric($p_index_kingdom))
                {
                    $this->idxKingdomField = $p_index_kingdom-1;
                }
                $this->sources=$p_sources;
                $this->languages = $p_languages;
            }            
            catch(Exeption $e)
            {
                print($e->getMessage());
            }
            print("DONE");

			
		}
		
		public function mapBooleanString($p_param)
		{
			$returned="";
			if(isset($p_param))
			{
				if(!$p_param)
				{
					$returned="False";
				}
				else
				{
					$returned="True";
				}
			}
			return $returned;
		}
        
		public function parseRow($p_i, $p_line_array, $p_worms_client, $p_mode_write=false, $p_output_file=null)
		{
			$canonical_set=false;
            $result=Array();
			$result_gbif=null;
            try
            {
					if($p_i==0 && $this->hasHeader)
					{
                        $this->headers=$p_line_array;
						//$p_i++;
						//continue;	
                        return;                        
					}
					elseif($p_i==0 && !$this->hasHeader)
					{
						$nb_fields=count($p_line_array);
						
						$this->headers=Array();
						for($j=0;$j<$nb_fields;$j++)
						{
							if($j==(int)$this->idxDataField)
							{
								$this->headers[]="Submitted scientific name";
							}
							else
							{
								$this->headers[]="Field ".(string)$j;
							}
							
						}
						
						
					}
					
					$sc_name=Encoding::toUTF8($p_line_array[$this->idxDataField]);
					$complete_name=$sc_name;
					
					
                    if(strlen(trim($sc_name))>0)
                    {
                        if(array_key_exists($sc_name, $this->holder)===FALSE||$p_mode_write)
                        { 
                            if(in_array("gbif", $this->sources))
                            {
                                $url_gbif=$this->url_webservice_gbif.urlencode($sc_name);
                                if(isset($this->idxKingdomField))
                                {
                                    if(is_numeric($this->idxKingdomField))
                                    {
                                        if((int)$this->idxKingdomField>0)
                                        {
                                            $kingdom=Encoding::toUTF8($p_line_array[$this->idxKingdomField]);
                                            $url_gbif=$url_gbif."&kingdom=".$this->kingdom_suffix.urlencode($kingdom);                                            
                                        }                                        
                                    }                                   
                                }
                               
                                
                                $tmp=file_get_contents($url_gbif);
                                                           
                                $result=Array();
                                
                                $gbif_parser = new ParseGBIFJSON($tmp, $sc_name);
                                $result_gbif= $gbif_parser->returnResult();
                                $result_gbif["gbif_url"] =$url_gbif;
                                $result=array_merge($result, $result_gbif);
                               
                                  
                                
                            }
							
							//GBIF vernacular
							if(in_array("gbif_vernacular", $this->sources))
                            {
                                $url_gbif=$this->url_webservice_gbif.urlencode($sc_name);
                                if(isset($this->idxKingdomField))
                                {
                                    if(is_numeric($this->idxKingdomField))
                                    {
                                        if((int)$this->idxKingdomField>0)
                                        {
                                            $kingdom=Encoding::toUTF8($p_line_array[$this->idxKingdomField]);
                                            $url_gbif=$url_gbif."&kingdom=".$this->kingdom_suffix.urlencode($kingdom);                                            
                                        }                                        
                                    }                                   
                                }
                               
                                
                                $tmp=file_get_contents($url_gbif);
                                                           
                                //$result=Array();
                                
                                $gbif_parser = new ParseGBIFJSONVernacular($tmp, $sc_name, $this->languages);
                                $result_gbif= $gbif_parser->returnResult();
                                $result=array_merge($result, $result_gbif);
                               
                                  
                                
                            }
							if(in_array("darwin", $this->sources))
                            {
								$results_darwin=Array();
								if($canonical_set===false)
								{
									$parserName = new GNNameParser($sc_name);
									$sc_name=$parserName->getCanonicalName();
									$canonical_set=true;
								}
								if(in_array("gbif", $this->sources))
								{
									$darwin_client = new ParseDarwinJSON($sc_name, $complete_name, true, $result);
								}
								else
								{
									$darwin_client = new ParseDarwinJSON($sc_name, $complete_name);
								}
								$results_darwin=$darwin_client->returnResult();
								$result=array_merge($result, $results_darwin);
							}
							if(in_array("iucn", $this->sources))
                            {
								$results_iucn=Array();
								if($canonical_set===false)
								{
									$parserName = new GNNameParser($sc_name);
									$sc_name=$parserName->getCanonicalName();
									$canonical_set=true;
								}
								if(isset($result_gbif))
								{									
									$iucn_client = new ParseIUCNJSON($this->iucn_token, $sc_name, $result_gbif['gbif_name_status'], $result_gbif['gbif_match_type'], $result_gbif['gbif_full_name']);
								}
								else
								{
									$iucn_client = new ParseIUCNJSON($this->iucn_token, $sc_name);
								}
								$results_iucn=$iucn_client->returnResult();
								$result=array_merge($result, $results_iucn);
							}
                            
                            //WORMS
                            if(in_array("worms",$this->sources))
                            {
                                $results_worms=Array();
                                
                                if($canonical_set===false)
								{
									$parserName = new GNNameParser($sc_name);
									$sc_name=$parserName->getCanonicalName();
									$canonical_set=true;
								}
                                $AphiaID=$p_worms_client->getAphiaID($sc_name);
                                
                                $results_worms["worms_id"]="";
                                $results_worms["worms_scientific_name"]="";
                                $results_worms["worms_author"]="";
                                $results_worms["worms_status"]="";
                                
                                $results_worms["worms_accepted_name"]="";
                                $results_worms["worms_accepted_author"]="";
                                $results_worms["worms_phylum"]="";
                                $results_worms["worms_class"]="";
                                $results_worms["worms_order"]="";
                                $results_worms["worms_family"]="";
                                $results_worms["worms_genus"]="";
                                $results_worms["worms_species"]="";
                                $results_worms["worms_subspecies"]="";
                                $results_worms["worms_is_marine"]="";
                                $results_worms["worms_is_brackish"]="";
                                $results_worms["worms_is_freshwater"]="";
                                $results_worms["worms_is_terrestrial"]="";										
                                $results_worms["worms_lsid"]="";
                                $results_worms["worms_url"]="";
                                if(is_numeric($AphiaID))
                                {
									if((integer)$AphiaID>0)
									{	
                                    
										$results_worms["worms_id"]=$AphiaID;
										$taxon=$p_worms_client->getAphiaRecordByID($AphiaID);
										if(is_object($taxon))
										{
											if(property_exists($taxon,"scientificname"))
											{
												$results_worms["worms_scientific_name"]=$taxon->scientificname;
											}
											if(property_exists($taxon,"authority"))
											{											
												$results_worms["worms_author"]=$taxon->authority;
											}
											if(property_exists($taxon,"status"))
											{											
												$results_worms["worms_status"]=$taxon->status;
												
											}
											
											
											if(property_exists($taxon,"valid_name"))
											{
												$results_worms["worms_accepted_name"]=$taxon->valid_name;
											}
											if(property_exists($taxon,"valid_authority"))
											{
												$results_worms["worms_accepted_author"]=$taxon->valid_authority;
											}
											
											$classification=$p_worms_client->getAphiaClassificationByID($AphiaID);
											if(is_object($classification))
											{
												$limit=40;
												$i=0;
												while($i<=$limit)
												{   
													if(property_exists($classification,"rank"))
													{
														switch(strtolower($classification->rank))
														{
															case "phylum":
																$results_worms["worms_phylum"]=$classification->scientificname;
																break;
															 case "class":
																$results_worms["worms_class"]=$classification->scientificname;
																break;
															 case "order":
																$results_worms["worms_order"]=$classification->scientificname;
																break;
															 case "family":
																$results_worms["worms_family"]=$classification->scientificname;
																break;
															 case "genus":
																$results_worms["worms_genus"]=$classification->scientificname;
																break;
															 case "species":
																$results_worms["worms_species"]=$classification->scientificname;
																break;
															 case "subspecies":
																$results_worms["worms_subspecies"]=$classification->scientificname;
																break;
														}
													}
													if(property_exists($classification,"child"))
													{
														
														$classification=$classification->child;
													}
													else
													{
														break;
													}
													
													$i++;
												}
												//$results_worms["worms_phylum"]= print_r(get_class_methods($classification));
											}
											if(property_exists($taxon,"isMarine"))
											{
												$results_worms["worms_is_marine"]=$this->mapBooleanString($taxon->isMarine);
											}
											if(property_exists($taxon,"isBrackish"))
											{
												$results_worms["worms_is_brackish"]=$this->mapBooleanString($taxon->isBrackish);
											}
											if(property_exists($taxon,"isFreshwater"))
											{
												$results_worms["worms_is_freshwater"]=$this->mapBooleanString($taxon->isFreshwater);
											}
											if(property_exists($taxon,"isTerrestrial"))
											{
												$results_worms["worms_is_terrestrial"]=$this->mapBooleanString($taxon->isTerrestrial);
											}
											if(property_exists($taxon,"lsid"))
											{
												$results_worms["worms_lsid"]=$taxon->lsid;
											}
											$results_worms["worms_url"]=$taxon->url;
										}
										 if(array_key_exists('background_style', $result)===FALSE&&array_key_exists('rgb_match_type', $result)===FALSE)
										 {
												$results_worms["rgb_match_type"]="#00ff00";
												$results_worms["background_style"]="";
												
										}
									}
                                }
                                        
                                $result=array_merge($result, $results_worms);
                            } // end of worms
                        
                        
                            if(array_key_exists("gbif_match_type", $result))
                            {
                                $result["gbif_match_type"]=str_replace("FUZZY", "MISSPELLING", $result["gbif_match_type"]);
                            }
                            $this->holder[$sc_name]=$result;
                        }
                        elseif(array_key_exists($sc_name, $this->holder)&&!$p_mode_write)
                        {
                            $result= $this->holder[$sc_name];
                        }
                            
                        $tmp=Array();
                        $tmp["parsed_data"]=$result;
                        //$tmp["parsed_data"]["url"]=$url_gbif;
                        $tmp["src_data"]=$p_line_array;
                        $this->write_in_db($tmp["src_data"],$tmp["parsed_data"]);
                        if(!$p_mode_write)
                        {
                           $this->completeResult[]=$tmp;
                        }
                        if($p_mode_write)
                        {
                            if($p_i==0)
                            {
                                $header_file=array_keys($result);
                                array_unshift($header_file, "taxon");
								$result=Encoding::toUTF8($header_file);
                                fwrite($p_output_file, implode("\t",$header_file ));
                                fwrite($p_output_file, "\r\n");
                            }
                            array_unshift($result, $p_line_array[$this->idxDataField] );
							$result=Encoding::toUTF8($result);
                            fwrite($p_output_file, implode("\t",$result ));
                            fwrite($p_output_file, "\r\n");
                        }
                             
                            
                   }//end if sc name
             }
             catch (SoapFault $e)
             {
                   echo 'Caught SOAP exception: ',  $e->getMessage(), "\n";
             }
             catch (Exception $e)
             {
                    echo 'Caught exception: ',  $e->getMessage(), "\n";
             }
		}
        
        protected function write_in_db($src_data, $result)
        {
            try
            {
                $db_driver=MyDB::instance();
                if($this->hasHeader)
				{
                        $src_data=array_combine($this->headers, $src_data);
                   
				}
                $tmp_row=array_merge($src_data, $result);
                $json_row = json_encode($tmp_row);
				if(!$this->deleted)
				{
					$sql= "DELETE FROM  public.taxon_checker WHERE date_data < (NOW() - INTERVAL '1 DAY')";
					$stmt = $db_driver->getPdo()->prepare($sql);
					$stmt->execute();
					$this->deleted=TRUE;
                }
				$sql= "INSERT INTO  public.taxon_checker (session, data, date_data, mail) VALUES (?, ?, NOW(), ?); ";
                $stmt = $db_driver->getPdo()->prepare($sql);
                $session_tmp= session_id();
                
                $stmt->execute([$session_tmp, $json_row, $this->mail]);
             }
             catch(PDOExeption $e)
            {
                print($e->getMessage());
            }
        }
		
		public function parseExternalArray(&$p_array, $p_key, $p_output_file)
		{
			print("GO");
			$this->idxDataField=$p_key;
			$this->idxKingdomField=null;
			$worms_client=null;
			if(in_array("worms",$this->sources))
            {
                $worms_client = new SoapClient($this->url_webservice_worms);
			}
			$i=0;
			foreach($p_array as $row)
			{
				
				$this->parseRow($i, $row, $worms_client,true, $p_output_file);
				$i++;
			}
              
            //$_SESSION[session_id()]["headers"] = $this->headers; 
            //$_SESSION[session_id()]["results"] = $this->completeResult; //$this->holder; 
			//$_SESSION[session_id()]["match_statistics"]=$this->getMatchingStatistics();				
            //$this->pager(1);
			

            
		}
        
        /*public function startClient()
        {
                    $this->gearman_client->doBackground('parseFile', session_id());
                    print("done start");

       }*/        
        
		
		public function parseFile()
		{
            $worms_client=null;
			if(in_array("worms",$this->sources))
            {
                $worms_client = new SoapClient($this->url_webservice_worms);

            }
			if($handler = fopen($this->srcFile, "r"))
			{
				$i=0;
				while(!feof($handler)) 
                {   
                    try {
                        $line_array = fgetcsv($handler,0, $this->delimiter);
                        $this->parseRow($i, $line_array, $worms_client);
					} 
                    catch (Exception $e) {
                        echo 'Caught exception: ',  $e->getMessage(), "\n";
                    }
					$i++;
					
				}
                //ksort($this->holder);
                $_SESSION[session_id()]["headers"] = $this->headers; 
                $_SESSION[session_id()]["results"] = $this->completeResult; //$this->holder; 
				//$_SESSION[session_id()]["match_statistics"]=$this->getMatchingStatistics();				
                //$this->pager(1);
				fclose($handler);
			}
			
			
		}
		
 
	
		
		
	
}
?>