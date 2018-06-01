<?php
header('Content-type:application/csv');
header('Content-disposition:attachment; filename="checked_taxonomy_for_darwin.txt"');
header("Pragma:no-cache");
session_id($_REQUEST['id']);
session_start();
    
$prefix_source="gbif_";
  
    $output = fopen('php://output', 'w');
    if(array_key_exists("results", $_SESSION)&&array_key_exists("headers", $_SESSION))
    {
       
        $returned=Array();
		$addedCols=array_keys($_SESSION['results'][0]['parsed_data']);
        $headers_check=Array();
        if(in_array($prefix_source."phylum",$addedCols))
        {
             $headers_check[$prefix_source."phylum"]="phylum";
        }
        if(in_array($prefix_source."class",$addedCols))
        {
             $headers_check[$prefix_source."class"]="class";
        }
        if(in_array($prefix_source."order",$addedCols))
        {
             $headers_check[$prefix_source."order"]="order";
        }
         if(in_array($prefix_source."family",$addedCols))
        {
             $headers_check[$prefix_source."family"]="family";
        }
         if(in_array($prefix_source."genus",$addedCols))
        {
             $headers_check["genus"]="genus";
        }
        if(in_array($prefix_source."species",$addedCols))
        {
             $headers_check[$prefix_source."species"]="species";
        }
        if(in_array($prefix_source."subspecies",$addedCols))
        {
             $headers_check[$prefix_source."subspecies"]="sub_species";
        }
        if(in_array($prefix_source."author",$addedCols))
        {
             $headers_check[$prefix_source."author"]="author_team_and_year";
        }
        
		fputcsv($output, $headers_check, "\t");
       
        foreach($_SESSION['results'] as $row)
        {
            $valueRow=$row['parsed_data'];
            //print_r( $valueRow);
            $rowTmp =Array();
            foreach($headers_check as $rankCheck=>$rankDarwinTemplate)
            {
                //$rowTmp[$rankDarwinTemplate]=$rankDarwinTemplate;
                if(array_key_exists($rankCheck, $valueRow))
                {
                    $rowTmp[$rankDarwinTemplate]=$valueRow[$rankCheck];
                }
            }
            
			fputcsv($output, $rowTmp, "\t");
        }
       
		
		fclose($output);
    }
?>