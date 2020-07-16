<?php
    header('Content-Type: application/json');

    
    $BASE_URL="/elasticsearch_cetaf_passport/";
    $ES="http://ursidae.rbins.be:9200/cetaf_passport/";
    $tmp_query=str_replace($BASE_URL,"", $_SERVER["REQUEST_URI"]);
    $tmp_query=str_replace("?".$_SERVER["QUERY_STRING"],"",$tmp_query);
   
    $parts=explode("/",$tmp_query);
    $init=false;
    $tmp_query2="";
    $escape=false;
    foreach($parts as $p)
    {
    
        if($init)
        {
            if(substr($p,0,1)=="_")
            {
                $tmp_query2.="/";
                $escape=false;
            }
            else
            {   
                if($escape)
                {
                    $tmp_query2.="%2F";
                }
                else
                {
                    $tmp_query2.="/";
                }
                $escape=true;
            }
        }
        $tmp_query2.=$p;
        $init=true;
    }
   
    
    $ch = curl_init( );
    $payload = json_encode( $_REQUEST);
    curl_setopt( $ch, CURLOPT_POSTFIELDS, $payload );
    curl_setopt($ch, CURLOPT_URL,$ES.$tmp_query2);
    curl_setopt( $ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));
    # Return response instead of printing.
    curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
    # Send request.
    $response = curl_exec($ch);
    curl_close($ch);

    print($response);
   

?>
