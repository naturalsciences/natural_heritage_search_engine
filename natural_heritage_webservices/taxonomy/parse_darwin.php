<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
require_once("csv_parser.php");
header('Content-Type: text/html; charset=utf-8');
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");
?>
<style>
 <?php include 'css/style.css'; ?> 
</style>
<style>
 body {
    font-size: 14px;
 }
</style>
<?php
 
    session_start();
	function parse_name($conn, $table, $field, $output, $sources)
	{
		
		
		$sql = "SELECT DISTINCT $field as taxon FROM $table ORDER BY $field LIMIT 150";
		$stmt = $conn->prepare($sql);
		
		$stmt->execute();
		$result=$stmt->fetchAll();
		
		
		$outputfile = fopen($output, "w");
		
		$myParser= new CSVParser(null, "taxon", false, "\t", null, $sources);
		
		$myParser->parseExternalArray($result, "taxon", $outputfile);
		$parsed_data =$_SESSION["results"];
		fclose($outputfile);
		
		
	}
	$server=$_REQUEST["ip_postgres"];
	$database=$_REQUEST["database"];
	$user=$_REQUEST["user"];
	$pwd=$_REQUEST["pwd"];
	$table=$_REQUEST["table"];
    $field=$_REQUEST["field"];
	$output=$_REQUEST["output"];
	$sources=Array();
	$has_headers = false;
	if(array_key_exists("source_gbif", $_REQUEST))
    {
        $sources[]="gbif";
    }
    if(array_key_exists("source_worms", $_REQUEST))
    {
        $sources[]="worms";
    }
	
	$dsn = "pgsql:host=$server;port=5432;dbname=$database;user=$user;password=$pwd";
 
	try{
	 // create a PostgreSQL database connection
	 $conn = new PDO($dsn);
	 
	 // display a message if connected to the PostgreSQL successfully
	 if($conn){
	 echo "Connected to the <strong>$database</strong> database successfully!";
		parse_name($conn, $table, $field, $output, $sources);
	 }
	}catch (PDOException $e){
	 // report error message
	 echo $e->getMessage();
	}
?>