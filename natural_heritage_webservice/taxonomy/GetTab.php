<?php
header('Content-type:application/csv');
header('Content-disposition:attachment; filename="checked_taxonomy.txt"');
header("Pragma:no-cache");

session_start();
    

  
    $output = fopen('php://output', 'w');
    if(array_key_exists("results", $_SESSION[$_REQUEST['id']])&&array_key_exists("headers", $_SESSION[$_REQUEST['id']]))
    {
       
        $returned=Array();
		//$addedCols=array_keys($_SESSION[$_REQUEST['id']]['results'][0]['parsed_data']);
        
		fputcsv($output, $_SESSION[$_REQUEST['id']]['headers'], "\t");
        foreach($_SESSION[$_REQUEST['id']]['results'] as $row)
        {
           //print_r($row['parsed_data']);
			fputcsv($output, array_merge($row['src_data'], $row['parsed_data']), "\t");
        }
       
		
		fclose($output);
		unsset($_SESSION[$_REQUEST['id']]['results']);
		unsset($_SESSION[$_REQUEST['id']]);		
    }

?>