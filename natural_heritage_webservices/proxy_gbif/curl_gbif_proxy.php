<?php
	require_once("restHelper_curl.php");
	$root_url="http://api.gbif.org/v0.9/species/match?";	
	$queryString=$_SERVER['QUERY_STRING'];
	
	$urlComplete=$root_url.$queryString;
	
	$json=rest_helper($urlComplete, 'Content-Type: application/json');
	header("Content-Type: application/json");	
	print($json[1]);

	//print($_SERVER['SERVER_NAME']);
?>
