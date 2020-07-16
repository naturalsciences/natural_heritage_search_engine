<?php
    header('Content-Type: application/json');
    $BASE_URL="/elasticsearch_cetaf_passport/";
    $ES="http://ursidae.rbins.be:9200/cetaf_passport/";
    function return_json($es, $id)
    {
        //print("<br/>");
        //print($es."_doc/".rawurlencode ($id));
        // print("<br/>");
        $ch = curl_init( );
    
    
        curl_setopt($ch, CURLOPT_URL,$es."_doc/".rawurlencode($id));
        curl_setopt( $ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));
        # Return response instead of printing.
        curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
        # Send request.
        $response = curl_exec($ch);
        curl_close($ch);
        $tmp_array=json_decode($response, true);
        //print_r($tmp_array);
        $doc=$tmp_array["_source"];
         //print("<br/>");
         
        //$children=$doc["direct_children"];
        $children_data=Array();
        if(array_key_exists("direct_children", $doc))
        {
            $children= $doc["direct_children"];
            foreach( $children as $elem)
            {
                //print($elem);
                $detail=return_json($es, urldecode($elem));
                $detail_array=json_decode($detail, true);
                //print_r($detail_array);
                
                $children_data[$detail_array["_id"]]=$detail_array["_source"];
            }
        }
       
        $doc["to_sub_collections"]=$children_data;
        $tmp_array["_source"]=$doc;
        $response=json_encode($tmp_array);
        return $response;
    }
    
    $tmp_id=$_REQUEST["id"];
   
     
    $response=return_json($ES,$tmp_id);
    print($response);
   
    
   
?>
