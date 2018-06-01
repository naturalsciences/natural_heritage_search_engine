<?php
	require_once("restHelper_curl.php");


	function filter_value_ci($p_array, $p_field, $p_value, &$p_cpt)
	{
		$returned='';		
		$cpt=0;
				
		foreach($p_array as $elem)
		{
			if(strtolower($elem[$p_field])==strtolower($p_value))
			{
				
				if($cpt==0)
				{				
					$returned=$elem;
				}
				$cpt++;
			}
		}
		$p_cpt=$cpt;
		return $returned;
		
	}

	function return_isset($param, $nameTag)
	{
		$returned="";
		if(isset($param))
		{
			if(strlen($param)>0)
			{
				$returned="<".$nameTag.">".$param."</".$nameTag.">";
			}
		}
		return $returned;
	}

	function return_Value($param)
	{
		$returned=FALSE;
		if(isset($param))
		{
			if(strlen($param)>0)
			{
				$returned=$param;
			}
		}
		return $returned;
	}

	function generate_gbif2col_classification_upperrank($p_array, $p_rankgbif, $p_rankcol)
	{
		$returned='';
		if(isset($p_array[$p_rankgbif]))
		{
			if(strlen($p_array[$p_rankgbif])>0)
			{
								
				$returned=return_isset($p_array[$p_rankgbif], $p_rankcol);
			}
		}
		return $returned;
	}

	function generate_gbif2col_classification($p_array)
	{
		$returned="<classification>";
		$returned.=generate_gbif2col_classification_upperrank($p_array, "kingdom", "Kingdom");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "phylum", "Phylum");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "clazz", "class");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "order", "Order");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "family", "Family");
		$returned.=generate_gbif2col_classification_upperrank($p_array, "genus", "Genus");
		$returned.="</classification>";
		return $returned;
	}


	function parsingName($p_response, $p_searchedName, $p_rootURL, $p_urlComplete, $p_cpt)
	{
		$returned ="";
		$flagSynonym=FALSE;
		if(isset($p_response["usageKey"]))
		{
			
			if(strlen($p_response["usageKey"])>0)
			{
				
				$returned .="<?xml version=\"1.0\" encoding=\"UTF-8\" ?>";			
				$returned .="<results id=\"\" name=\"".$p_searchedName."\">";
				$returned .=return_isset(htmlspecialchars($p_urlComplete),"gbif_url");
				$returned .=return_isset($p_cpt,"gbif_results");
				
				$returned .="<result>";
				$returned .="<id>".$p_response["usageKey"]."</id>";
				$returned .=return_isset($p_response["note"],"gbif_note");				
				$returned .= return_isset(htmlspecialchars($p_response["matchType"]),"matchType");
				$returned .= return_isset($p_response["rank"],"rank");
				$rankInGBIF=strtolower($p_response["rank"]);
				if($rankInGBIF=="class")
				{
					$rankInGBIF="clazz";			
				}
				$accepted_name=$p_response[$rankInGBIF];
				if(return_Value($p_response["synonym"]=="1"))
				{
					$flagSynonym=TRUE;
				}
				if($flagSynonym)
				{
					//print_r($response);
					$newQueryString="name=".str_replace(' ','+',$accepted_name)."&verbose=true";
				
					$jsonAccepted=rest_helper($p_rootURL.$newQueryString, 'Content-Type: application/json');
				
					$responseJsonAccepted=json_decode($jsonAccepted[1], TRUE);


					$author=trim(str_ireplace($accepted_name,'',$responseJsonAccepted["scientificName"]) );
					$returned .=return_isset("synonym","name_status");
					$returned .="<accepted_name>";
					$returned .=return_isset(htmlspecialchars($author),"author");
					$returned .=return_isset($accepted_name,"name");
					$returned .= generate_gbif2col_classification($responseJsonAccepted);
					$returned .="</accepted_name>";
				}
				else
				{	$author=trim(str_ireplace($p_searchedName,'',$p_response["scientificName"]) );
					$returned .=return_isset(htmlspecialchars($author),"author");
					$returned .= return_isset("accepted name","name_status");
					$returned .=return_isset($accepted_name,"name");
					$returned .=generate_gbif2col_classification($p_response);
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
	$response=json_decode($json[1], TRUE);
	
	if(isset($response["usageKey"]))
	{
		if(strlen($response["usageKey"])>0)
		{
			
			$flagFound=TRUE;
			$displayedXML=parsingName($response, $searchedName, $root_url, $urlComplete, 1);
			print($displayedXML);
		}	
	}
	elseif(isset($response['note']))
	{
		if(strlen($response['note'])>0)
		{
			if(strtolower($response['note'])!="no match because of too little confidence")
			{
				$flagFound=TRUE;
				
				if(is_int(strpos(strtolower($response['note']),"multiple equal matches")))
				{
					
					$alternatives=$response['alternatives'];
					
					if(isset($_REQUEST['custom_check_rank'])===FALSE && isset($_REQUEST['custom_check_value'])===FALSE)
					{
						$displayedXML=parsingName($alternatives[0], $searchedName, $root_url, $urlComplete, "several values (no filter)");
						print($displayedXML);
					}
					else
					{
						
						$gbifCpt=0;
						$filteredObj=filter_value_ci($alternatives, $_REQUEST['custom_check_rank'], $_REQUEST['custom_check_value'], $gbifCpt);
						$displayedXML=parsingName($filteredObj, $searchedName, $root_url, $urlComplete, $gbifCpt);
						print($displayedXML);
	
					}
				}
			}
		}
	}
	if($flagFound===FALSE)
	{
		print("not found");
	}

	

?>
