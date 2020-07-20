<?php
    header('Content-Type: application/json');
	ob_start();
    $BASE_URL="/elasticsearch_cetaf_passport/";
    $ES_INSTITUTION="http://ursidae.rbins.be:9200/cetaf_passport/_search?q=main_type:institution&size=";
	$ES_COLLECTION="http://ursidae.rbins.be:9200/cetaf_passport/_search?q=main_type:collection&size=";
	$institution_list=Array();
	$collection_list=Array();
	$MAX_RECURSION=50;
	$results=Array();
    function return_json($es, $size=10000)
    {
        
	    $tmp_url=$es.$size;
		
        $ch = curl_init( );
        
    
        curl_setopt($ch, CURLOPT_URL, $tmp_url);
        curl_setopt( $ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));
        # Return response instead of printing.
        curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
        # Send request.
        $response = curl_exec($ch);
        curl_close($ch);
        $tmp_array=json_decode($response, true);
		
		
		return $tmp_array;
    }
    
	
	function recursion_sub_collection($doc, $id, $level)
	{
		global $collection_list;
		global $MAX_RECURSION;
		
		if($level<=$MAX_RECURSION)
		{
			 $doc["to_sub_collections"][]=Array();
			 $children_data=Array();
			
			 if(array_key_exists("direct_children", $doc))
			{
				$children= $doc["direct_children"];
				foreach( $children as $sub_coll_id)
				{
					$detail_array=$collection_list[$sub_coll_id];
					$detail=recursion_sub_collection($detail_array,$sub_coll_id, $level+1);					
					$children_data[$sub_coll_id]=$detail;
				}
			}
			
			$doc["to_sub_collections"]=$children_data;		
		}		
        return $doc;
	}
       
     
    $response_coll=return_json($ES_COLLECTION);
	
	foreach($response_coll["hits"]["hits"] as $elem)
	{
		$collection_list[$elem["_id"]]=$elem["_source"];
	}
	
	$response_inst=return_json($ES_INSTITUTION);
	
	foreach($response_inst["hits"]["hits"] as $elem)
	{
		$doc=$elem["_source"];
		$children_data=Array();
        $doc=recursion_sub_collection($doc, $elem['_id'], 0);
		$results[$elem["_id"]]=$doc;
	}
    ksort($results);
    print(json_encode($results));
    ob_flush();
   
?>