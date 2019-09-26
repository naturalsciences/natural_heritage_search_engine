
<?php
 
    ini_set('display_errors', 1);
	ini_set('display_startup_errors', 1);
	error_reporting(E_ALL);
	require_once("csv_parser.php");
	
	
	$server="salmoneus.rbins.be";
	$database="darwin2";
	$user="postgres";
	$pwd='CeBmPadYC';
	$table="darwin2.taxonomy";
    $field="name";
	$output="/var/developments/output_darwin_worms/full_darwin_compare_worms_2.txt";
	$sources=Array();
	//$sources[]="gbif";
	$sources[]="worms";
	
	function parse_name($conn, $table, $field, $output, $sources)
	{
		
		
		$sql = "SELECT  regexp_replace(taxon, '\t', ' ','g') as taxon FROM (SELECT DISTINCT $field as taxon FROM $table ORDER BY $field) a ";
		$stmt = $conn->prepare($sql);
		
		$stmt->execute();
		$result=$stmt->fetchAll();
		
		
		$outputfile = fopen($output, "w");
		
		$myParser= new CSVParser(null, "taxon", false, "\t", null, $sources);
		
		$myParser->parseExternalArray($result, "taxon", $outputfile);
		$parsed_data =$_SESSION["results"];
		fclose($outputfile);
		
		
	}
	
	
	$has_headers = false;
	
	
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