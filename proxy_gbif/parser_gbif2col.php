<?php
	require_once("restHelper_curl.php");
	

	function get_json_taxon($p_nameKey, $p_url="http://api.gbif.org/v1/species/")
	{
		$returned=NULL;
		if(is_int($p_nameKey))
		{
			$urlComplete=$p_url.$p_nameKey;
			$json=rest_helper($urlComplete, 'Content-Type: application/json');
			$response=json_decode($json[1], TRUE);
			$returned=$response;
		}
		return $returned;
	
	}



	function filter_value_ci($p_array, $p_field, $p_value, &$p_cpt, $treshold=5)
	{
		$returned='';		
		$cpt=0;
		$arrayRanks=Array();
		$arrayRanks[]="canonicalName";
		$arrayRanks[]="rank";
		$arrayRanks[]="matchType";
		$arrayRanks[]="kingdom";
		$arrayRanks[]="phylum";		
		$arrayRanks[]="class";
		$arrayRanks[]="order";
		$arrayRanks[]="family";
		$arrayRanks[]="genus";
		$arrayRanks[]="species";	
		foreach($p_array as $elem)
		{

			if(strtolower($elem[$p_field])==strtolower($p_value))
			{
				
				if($cpt==0)
				{				
					$returned=$elem;
				}
				else
				{
					
					addRanks($returned, $elem, $cpt, $treshold, $arrayRanks);
				}
				$cpt++;
			}
		}
		if($cpt>0)
		{
			foreach($arrayRanks as $rankTmp)
			{
				if(isset($returned[$rankTmp]))
				{
					if($returned[$rankTmp]=="/...")
					{
						unset($returned[$rankTmp]);
					}
				}
			}
		}

		$p_cpt=$cpt;
		
		return $returned;
		
	}
	
	//ftheeten 2018 05 018 (for altenratives with fuzzy matching)
	function no_filter_value_ci($p_array,  &$p_cpt, $treshold=5)
	{
		$returned='';		
		$cpt=0;
		$arrayRanks=Array();
		$arrayRanks[]="canonicalName";
		$arrayRanks[]="rank";
		$arrayRanks[]="matchType";
		$arrayRanks[]="kingdom";
		$arrayRanks[]="phylum";		
		$arrayRanks[]="class";
		$arrayRanks[]="order";
		$arrayRanks[]="family";
		$arrayRanks[]="genus";
		$arrayRanks[]="species";	
		foreach($p_array as $elem)
		{

			
				
				if($cpt==0)
				{				
					$returned=$elem;
				}
				else
				{
					
					addRanks($returned, $elem, $cpt, $treshold, $arrayRanks);
				}
				$cpt++;
			
		}
		if($cpt>0)
		{
			foreach($arrayRanks as $rankTmp)
			{
				if(isset($returned[$rankTmp]))
				{
					if($returned[$rankTmp]=="/...")
					{
						unset($returned[$rankTmp]);
					}
				}
			}
		}

		$p_cpt=$cpt;
		
		return $returned;
		
	}
	
	function addRanks(&$p_response, $elem, $key, $keyMax, $arrayRanks)
	{
		
		foreach($arrayRanks as $rank)
		{
			$appendix="";
			
	
			if($key<$keyMax)			
			{
				if(isset($elem[$rank]))
				{
					$appendix="/".$elem[$rank];
				}
				//for synonym
				if($rank=="rank")
				{
					if($elem["synonym"]===TRUE)
					{
						$appendix=$appendix." (syn.)";
					}
				}				
				
			}
			elseif($key==$keyMax)
			{
				$appendix="/...";
			}
				
			if(isset($p_response[$rank]))
			{
				$p_response[$rank]=$p_response[$rank].$appendix;		
			}
			else
			{
				$p_response[$rank]=$appendix;
			}
			
		}
	
	}

	function return_isset($param, $nameTag)
	{
		
		$returned="<".$nameTag."></".$nameTag.">";		
		if(isset($param))
		{
			if(strlen($param)>0)
			{
				$returned="<".$nameTag.">".$param."</".$nameTag.">";
			}
			
		}
		return $returned;
	}

	function starts_with_upper($p_str)
	{
		$chr=mb_substr($p_str,0,1, "UTF-8");
		return mb_strtolower($chr, "UTF-8")!=$chr;
	}

	function check_is_author_and_display_xml($param, $nameTag)
	{
		//buggy, ex: "van der Graaf" not found
		/*if(starts_with_upper($param)||substr(trim($param),0,1)=="(")
		{
			
			return return_isset($param, $nameTag);
		}
		else
		{
			
			return return_isset("", $nameTag);
		}*/
		return return_isset($param, $nameTag);
		
	}

	function return_Value($param)
	{
		$returned=FALSE;
		if(isset($param))
		{
			if(strlen($param)>0)
			{
				$returned=htmlspecialchars($param);
			}
		}
		return $returned;
	}

	function generate_gbif2col_classification_upperrank($p_array, $p_rankgbif, $p_displayedRank=NULL)
	{
		$returned='';
		if(isset($p_array[$p_rankgbif]))
		{
			if(strlen($p_array[$p_rankgbif])>0)
			{
				if(isset($p_displayedRank))
				{
					$dislayedRank=$p_displayedRank;
				}
				else
				{
					$dislayedRank=$p_rankgbif;				
					if($p_rankgbif=="class")
					{
						$dislayedRank="class";
					}
				}
				$returned.="<taxon>";
				$returned.=return_isset($p_array[$p_rankgbif] ,"name");
				$returned.=return_isset(ucfirst($dislayedRank) ,"rank");	
				$returned.="</taxon>";				
				
			}
		}
		return $returned;
	}

	function generate_gbif2col_classification($p_array, $p_rankTag="rank")
	{

		$returned="<classification>";
		$returned.=generate_gbif2col_classification_upperrank($p_array, "kingdom", "Kingdom");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "phylum", "Phylum");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "class", "Class");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "order", "Order");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "family", "Family");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "genus", "Genus");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "species", "Species");
		
		if(
			strtolower($p_array[$p_rankTag])=="subspecies"
			||
			strtolower($p_array[$p_rankTag])=="infraspecies"
			||
			strtolower($p_array[$p_rankTag])=="variety"
		)
		{
			if(isset($p_array["species"]))
			{
				$returned.=generate_gbif2col_classification_upperrank($p_array, "canonicalName", "Subspecies");
			}
		}
		$returned.="</classification>";
		return $returned;
	}


	function getHigherOfFuzzy($p_searchedName,  $p_fuzzyCorrection, $p_rootURL, $p_response, $p_responseTaxon)
	{
		$returned['flagCorrected']=FALSE;
		$tabWords=explode(" ", $p_searchedName);
		$tabCorrection=explode(" ",$p_fuzzyCorrection );
		{
			if(count($tabWords)>1)
			{
				$upperName=Array();
				$flagGo=FALSE;
				if(count($tabWords)==count($tabCorrection))
				{
					for($i=0; $i<count($tabWords)-1;$i++)
					{
						$upperName[]=$tabWords[$i];
						if($tabWords[$i]!=$tabCorrection[$i])
						{
							$flagGo=TRUE;
						}
					}
				}
				else
				{
					for($i=0; $i<count($tabWords)-1;$i++)
					{
						$upperName[]=$tabWords[$i];
					}
					$flagGo=TRUE;
				}
				
				if($flagGo===TRUE)
				{
					$newName=implode(" ",$upperName);
					$tmpRequest=$_GET;
					$tmpRequest['name']=$newName;
					$tmpRequest2=Array();
					
					
					$queryString=http_build_query($tmpRequest);
					$urlComplete=$p_rootURL.$queryString;
					$json=rest_helper($urlComplete, 'Content-Type: application/json');
			
					$flagFound=FALSE;
					$newResponse=json_decode($json[1], TRUE);
					if(strtolower($newResponse["matchType"])=="exact")
					{
						$newResponse["matchType"]="HIGHERRANK (".$newResponse["canonicalName"].") OR FUZZY in another HIGHERRANK (suggestion for correction at ".$p_response["rank"]." level: ".$p_fuzzyCorrection.")";
						$returned=$newResponse;
						$newResponseTaxon=get_json_taxon($newResponse["usageKey"]);
						$returned['flagCorrected']=TRUE;
						$returned['response']=$newResponse;
						$returned['responseTaxon']= $newResponseTaxon;
					}
				}
			}	
		}
		return $returned;
	}
	
	function parsingName($p_response,  $p_responseTaxon, $p_searchedName, $p_rootURL, $p_urlComplete, $p_cpt)
	{
		$returned ="";
		$flagSynonym=FALSE;
		if(isset($p_response["usageKey"]))
		{
			
			if(strlen($p_response["usageKey"])>0)
			{
				if(return_Value($p_response["synonym"]=="1"))
				{
					$flagSynonym=TRUE;
				}
				if(strtolower($p_response["matchType"])=="fuzzy")
				{
					$testFuzzy=getHigherOfFuzzy($p_searchedName, $p_responseTaxon["canonicalName"], $p_rootURL, $p_response, $p_responseTaxon);
					if($testFuzzy['flagCorrected']===TRUE)
					{
						$p_response=$testFuzzy['response'];
						$p_responseTaxon=$testFuzzy['responseTaxon'];
					}
					if($flagSynonym===TRUE)
					{
						$p_response["matchType"]=$p_response["matchType"]. " (".$p_responseTaxon["canonicalName"].") + synonymy";
					}
				}
				
				if(strtolower($p_responseTaxon['taxonomicStatus'])=="doubtful")
				{
					$p_response["matchType"]="DOUBTFUL (".$p_response["matchType"].")";
				}
				
				$returned .="<?xml version=\"1.0\" encoding=\"UTF-8\" ?>";			
				$returned .="<results id=\"\" name=\"".$p_searchedName."\">";
				$returned .=return_isset(htmlspecialchars($p_urlComplete),"gbif_url");
				$returned .=return_isset($p_cpt,"gbif_results");
				
				$returned .="<result>";
				$returned .="<id>".$p_response["usageKey"]."</id>";
				$returned .=return_isset($p_response["note"],"gbif_note");
				$returned .=return_isset($p_response["confidence"],"confidence");				
				$returned .= return_isset(htmlspecialchars($p_response["matchType"]),"matchType");
				$returned .= return_isset($p_response["rank"],"rank");
				$rankInGBIF=strtolower($p_response["rank"]);
				if($rankInGBIF=="class")
				{
					$rankInGBIF="class";			
				}


				
				if($flagSynonym||strtolower($p_responseTaxon['taxonomicStatus'])=="synonym")
				{

					$keyAccepted=NULL;
					if(isset($p_responseTaxon['acceptedKey']))
					{
						if(is_int($p_responseTaxon['acceptedKey']))
						{
							$keyAccepted=$p_responseTaxon['acceptedKey'];
						}
					}
					elseif(isset($p_responseTaxon['speciesKey']))
					{
						if(is_int($p_responseTaxon['speciesKey']))
						{
							$keyAccepted=$p_responseTaxon['speciesKey'];
						}
					}
					if(isset($keyAccepted))
					{
						$responseJsonAccepted= get_json_taxon($keyAccepted);
						$authorSearchedName=$p_responseTaxon['authorship'];
						$responseSearchedName=$p_responseTaxon["canonicalName"];
						$accepted_name=$responseJsonAccepted["canonicalName"];
						$returned .=return_isset(htmlspecialchars($authorSearchedName),"author");
						$returned .=return_isset(htmlspecialchars($responseSearchedName),"name");
						$returned .=return_isset("synonym","name_status");
						if(isset($p_responseTaxon['publishedIn']))
						{
							$returned .=return_isset(htmlspecialchars($p_responseTaxon['publishedIn']),"published_in");
						}
						if(isset($p_responseTaxon['accordingTo']))
						{
							$returned .=return_isset(htmlspecialchars($p_responseTaxon['accordingTo']),"according_to");
						}
						$returned .="<accepted_name>";
						$returned .=return_isset(htmlspecialchars($responseJsonAccepted["authorship"]),"author");
						$returned .=return_isset(htmlspecialchars($accepted_name),"name");
						$returned .=return_isset("accepted name","name_status");
						$returned .=return_isset(htmlspecialchars(ucfirst(strtolower($responseJsonAccepted["rank"]))),"rank");

						$returned .= generate_gbif2col_classification($responseJsonAccepted);
						if(isset($responseJsonAccepted['publishedIn']))
						{
							$returned .=return_isset(htmlspecialchars($responseJsonAccepted['publishedIn']),"published_in");
						}
						if(isset($responseJsonAccepted['accordingTo']))
						{
							$returned .=return_isset(htmlspecialchars($responseJsonAccepted['accordingTo']),"according_to");
						}
						$returned .="</accepted_name>";
					}
				}
				elseif(strtolower($p_responseTaxon['taxonomicStatus'])=="accepted"||strtolower($p_responseTaxon['taxonomicStatus'])=="doubtful")
				{	

									
					$author=$p_responseTaxon['authorship'];
					$accepted_name=$p_responseTaxon['canonicalName'];
					$returned .=check_is_author_and_display_xml(htmlspecialchars($author),"author");
					$returned .= return_isset("accepted name","name_status");
					$returned .=return_isset($accepted_name,"name");
					$returned .=generate_gbif2col_classification($p_responseTaxon);
					if(isset($p_responseTaxon['publishedIn']))
					{
						$returned .=return_isset(htmlspecialchars($p_responseTaxon['publishedIn']),"published_in");
					}
					if(isset($p_responseTaxon['accordingTo']))
					{
						$returned .=return_isset(htmlspecialchars($p_responseTaxon['accordingTo']),"according_to");
					}
				}

				else
				{

					$returned .= return_isset("unknown","name_status");
					$returned .=return_isset("Error: neither accepted name nor synonym","name");
				}
				$returned .="</result>";
				$returned .="</results>";
			}	
		}

		return $returned;
	}
	
	$root_url="http://api.gbif.org/v0.9/species/match?";	
	
	$queryString=$_SERVER['QUERY_STRING'];
	
	$urlComplete=$root_url.$queryString;

	$accepted_name=NULL;
	$json=rest_helper($urlComplete, 'Content-Type: application/json');
	
	header("Cache-Control: no-cache, must-revalidate"); // HTTP/1.1
	header("Expires: Sat, 26 Jul 1997 05:00:00 GMT"); // Date in the past
	header("Content-Type: text/xml", "UTF-8" );

	
	$flagFound=FALSE;
	//print_r(json_decode($json[1], true));
	$searchedName=$_REQUEST["name"];
	$noResultMSG="<?xml version=\"1.0\" encoding=\"UTF-8\" ?><results name=\"".$searchedName."\" total_number_of_results=\"0\" total_number_of_results_returned=\"0\" start=\"0\" error_message=\"No name found (wrapping GBIF)\">No results</results>";
	$response=json_decode($json[1], TRUE);
	$flagGo=TRUE;
	$flagAlternative=FALSE;
	if(isset($_REQUEST['custom_check_rank'])===TRUE && isset($_REQUEST['custom_check_value'])===TRUE)
	{
		if(strtolower($response["rank"])==strtolower($_REQUEST['custom_check_rank'])&&strtolower($response["rank"])==strtolower($_REQUEST['custom_check_rank']))
		{
			if(isset($response['alternatives'])===FALSE)
			{			
				$flagGo=FALSE;
				//$flagFound=FALSE;
			}
			else
			{
				$flagAlternative=TRUE;
			}
		}
		
	}

	if(isset($response['alternatives'])&&strtolower($response['matchType'])=='higherrank'&&$flagAlternative===TRUE)
	{
		$alternatives=$response['alternatives'];
				
		if(isset($_REQUEST['custom_check_rank'])===FALSE && isset($_REQUEST['custom_check_value'])===FALSE)
		{
			$responseNameDirect=get_json_taxon($alternatives[0]["usageKey"]);
			$displayedXML=parsingName($alternatives[0],$responseNameDirect, $searchedName, $root_url, $urlComplete, "several values (no filter)");
			print($displayedXML);
		}
		else
		{
			$flagFound=TRUE;	
			$gbifCpt=0;
			$filteredObj=filter_value_ci($alternatives, $_REQUEST['custom_check_rank'], $_REQUEST['custom_check_value'], $gbifCpt);

			//relevant alternatives
			if($gbifCpt>1)
			{
				$filteredObj["note"]=$filteredObj["note"]. " + BEWARE several responses found!";
				$filteredObj["matchType"]=$filteredObj["matchType"]. " + BEWARE several responses found!";
			}
			//$responseNameDirect=get_json_taxon($filteredObj["usageKey"]);
			$responseNameDirect=$filteredObj;
			$responseNameDirect["taxonomicStatus"]="accepted";
			$displayedXML=parsingName($filteredObj, $responseNameDirect, $searchedName, $root_url, $urlComplete, $gbifCpt);
			if($gbifCpt>0)
			{	
								
				print($displayedXML);
			}
			else
			{
				print($noResultMSG);
			}
	
		}
	}
	//ftheeten 2015 05 18
	if(isset($response['alternatives'])===TRUE)
	{
		
		$flagAlternative=TRUE;
		$alternatives=$response['alternatives'];
		$flagFound=TRUE;	
			$gbifCpt=0;
			$filteredObj=no_filter_value_ci($alternatives, $gbifCpt);

			//relevant alternatives
			if($gbifCpt>1)
			{
				$filteredObj["note"]=$filteredObj["note"]. " + BEWARE several responses found!";
				$filteredObj["matchType"]=$filteredObj["matchType"]. " + BEWARE several responses found!";
			}
			//$responseNameDirect=get_json_taxon($filteredObj["usageKey"]);
			$responseNameDirect=$filteredObj;
			$responseNameDirect["taxonomicStatus"]="accepted";
			$displayedXML=parsingName($filteredObj, $responseNameDirect, $searchedName, $root_url, $urlComplete, $gbifCpt);
			if($gbifCpt>0)
			{	
								
				print($displayedXML);
			}
			else
			{
				print($noResultMSG);
			}
	}
	elseif(isset($response["usageKey"])&&$flagGo===TRUE)
	{
		if(strlen($response["usageKey"])>0)
		{
			
			
			$flagFound=TRUE;
			if(isset($_REQUEST['custom_check_rank'])===FALSE && isset($_REQUEST['custom_check_value'])===FALSE)
			{
				$responseNameDirect=get_json_taxon($response["usageKey"]);
				$displayedXML=parsingName($response,  $responseNameDirect, $searchedName, $root_url, $urlComplete, 1);
				print($displayedXML);
			}
			else
			{
				//several name-> fikter	
				$gbifCpt=0;
				$tmpArray=Array();
				$tmpArray[]=$response;
				//because problem in GBIF reply: alternatives of an exat name may be also exact and beter ranked
				$flagNestedAlt=FALSE;
				if(isset($response['alternatives']))//&&strtolower($response['matchType'])=="exact")
				{
					if(count($response['alternatives'])>0)
					{
						foreach($response['alternatives'] as $elem)
						{
							if(strtolower($elem['matchType'])=="exact")
							{	
								//if(isset($_REQUEST['custom_check_rank']) &&isset($elem[$_REQUEST['custom_check_rank']]))		
								//{	
								//	if(strtolower($elem[$_REQUEST['custom_check_rank']])==strtolower($_REQUEST['custom_check_value']))
								//	{			
										$tmpArray[]=$elem;
										$flagNestedAlt=TRUE;
								//	}
								//}
							}
						}
					}
				}
				$filteredObj=filter_value_ci($tmpArray, $_REQUEST['custom_check_rank'], $_REQUEST['custom_check_value'], $gbifCpt);
				if($flagNestedAlt===FALSE||$gbifCpt==1)
				{
					$responseNameDirect=get_json_taxon($filteredObj["usageKey"]);
				
				}
				else
				{
					//relevant alternative
					$filteredObj["matchType"]=$filteredObj["matchType"]. " + BEWARE several responses found!";
					$filteredObj["note"]=$filteredObj["note"]. " + BEWARE several responses found!";
					//$responseNameDirect=get_json_taxon($filteredObj["usageKey"]);
					$responseNameDirect=$filteredObj;
					$responseNameDirect["taxonomicStatus"]="accepted";
				}
				$displayedXML=parsingName($filteredObj,$responseNameDirect, $searchedName, $root_url, $urlComplete, $gbifCpt);
				if($gbifCpt>0)
				{			
					print($displayedXML);
				}
				else
				{
					print($noResultMSG);				
				}
			}			
			
		}	
	}
	elseif(isset($response['note'])&&$flagGo===TRUE)
	{
		if(strlen($response['note'])>0)
		{
			//if(strpos($response['note'], "Multiple equal matches")==0)
			//{
				//if(strtolower($response['note'])!="no match because of too little confidence"&&strtolower($response['matchType'])!="none")
				if(strtolower($response['note'])!="no match because of too little confidence")
				{
									
					$flagFound=TRUE;
				
					if(is_int(strpos(strtolower($response['note']),"multiple equal matches")))
					{
					
						$alternatives=$response['alternatives'];
					
						if(isset($_REQUEST['custom_check_rank'])===FALSE && isset($_REQUEST['custom_check_value'])===FALSE)
						{
							$responseNameDirect=get_json_taxon($alternatives[0]["usageKey"]);
							$displayedXML=parsingName($alternatives[0],$responseNameDirect, $searchedName, $root_url, $urlComplete, "several values (no filter)");
							print($displayedXML);
						}
						else
						{
						
							$gbifCpt=0;
							$filteredObj=filter_value_ci($alternatives, $_REQUEST['custom_check_rank'], $_REQUEST['custom_check_value'], $gbifCpt);
							$responseNameDirect=get_json_taxon($filteredObj["usageKey"]);
							$displayedXML=parsingName($filteredObj, $responseNameDirect, $searchedName, $root_url, $urlComplete, $gbifCpt);
							if($gbifCpt>0)
							{						
								print($displayedXML);
							}
							else
							{
								print($noResultMSG);
							}
	
						}
					}
				}
				else
				{
					$flagFound=TRUE;
					if(isset($_REQUEST['custom_check_rank'])===FALSE && isset($_REQUEST['custom_check_value'])===FALSE)
					{
						$responseNameDirect=get_json_taxon($response["usageKey"]);
						$displayedXML=parsingName($response, $responseNameDirect, $searchedName, $root_url, $urlComplete, 1);
						print($displayedXML);
					}
					else //too little confidence
					{
					
						$gbifCpt=0;
						$tmpArray=Array();
						$tmpArray[]=$response;
						$filteredObj=filter_value_ci($tmpArray, $_REQUEST['custom_check_rank'], $_REQUEST['custom_check_value'], $gbifCpt);
				
						$displayedXML=parsingName($filteredObj, $searchedName, $root_url, $urlComplete, $gbifCpt);
						if($gbifCpt>0)
						{				
							print($displayedXML);
						}
						else
						{
							print($noResultMSG);				
						}
					}	
				}
			//}
			//elseif($response['matchType']!='NONE')
			//{
			//	$flagFound==TRUE;
			//}
		}
	}
	
	if($flagFound===FALSE)
	{
		print($noResultMSG);
	}

	

?>
