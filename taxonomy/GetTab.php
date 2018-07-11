<?php
header('Content-type:application/csv');
header('Content-disposition:attachment; filename="checked_taxonomy.txt"');
header("Pragma:no-cache");
session_id($_REQUEST['id']);
session_start();
    

  
    $output = fopen('php://output', 'w');
    if(array_key_exists("results", $_SESSION)&&array_key_exists("headers", $_SESSION))
    {
       
        $returned=Array();
		$addedCols=array_keys($_SESSION['results'][0]['parsed_data']);
        
		fputcsv($output, array_merge($_SESSION['headers'],$addedCols), "\t");
        foreach($_SESSION['results'] as $row)
        {
           //print_r($row['parsed_data']);
			fputcsv($output, array_merge($row['src_data'], $row['parsed_data']), "\t");
        }
       
		
		fclose($output);
    }
?>