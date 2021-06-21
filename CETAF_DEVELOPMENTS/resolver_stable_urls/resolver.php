<?php

$base_url="/elasticsearch_cetaf_passport/institutions_full/";

function content_curl($url)
{
	header('Location: '.$url);
}

function go_curl($url)
{
	$ch = curl_init( );
	curl_setopt($ch, CURLOPT_URL,$url);
    curl_setopt( $ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));
    # Return response instead of printing.
    curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
    # Send request.
    $response = curl_exec($ch);
    curl_close($ch);

	$data=json_decode($response, true);
	
	$forward=false;
	$forward_url=null;
	if(array_key_exists("hits", $data))
	{
		if(array_key_exists("hits", $data["hits"]))
		{
			if(count( $data["hits"]["hits"])>0)
			{
				if(array_key_exists("_id", $data["hits"]["hits"][0]))
				{
					$forward=true;
					$forward_url=$data["hits"]["hits"][0]["_id"];
				}
			}
		}
	}
    if($forward)
	{
		content_curl($forward_url);
	}
	else
	{
		header('HTTP/1.0 404 Not Found', true, 404);
		echo "Identifier not found.\n";
		die();
	}
}

if(array_key_exists("grid_id", $_REQUEST))
{
	$grid_id=$_REQUEST["grid_id"];
	$param="_search?q=identification_fields.grid_id:%22".urlencode($grid_id)."%22";
	$url= "https://".$_SERVER['SERVER_NAME'].$base_url.$param;
	//print($url);
	go_curl($url);
}
elseif(array_key_exists("wikidata_id", $_REQUEST))
{
	$wikidata_id=$_REQUEST["wikidata_id"];
	$param="_search?q=identification_fields.wikidata_id:%22".urlencode($wikidata_id)."%22";
	$url= "https://".$_SERVER['SERVER_NAME'].$base_url.$param;
	//print($url);
	go_curl($url);
}

?>