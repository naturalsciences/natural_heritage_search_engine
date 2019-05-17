<?php
require_once("csv_parser.php");
require_once("pager.php");
require_once("get_data_db.php");
header('Content-Type: application/json; charset=utf-8');
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");

//session_start();  

  
//print($_REQUEST['id']);  
if(array_key_exists('id', $_REQUEST))
{
	$db_parser=new GetDataDB();
	$cpt=$db_parser->countData($_REQUEST['id']);
    print(json_encode(array("cpt"=>$cpt)));
	
}

?>

