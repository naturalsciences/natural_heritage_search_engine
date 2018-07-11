<?php
//ini_set('display_errors', 1);
//ini_set('display_startup_errors', 1);
//error_reporting(E_ERROR);
require_once("csv_parser.php");
require_once("pager.php");
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

function handleParsedCSV($p_page)
{
    $pager= new HTMLPager($_SESSION["results"], "50", "./parse_file.php?page=", $_SESSION["headers"]);
    print("PAGE = ". $p_page." ");
    print("NB_PAGES = ".  $pager->getNbPages() );
    $pager->get_page($p_page);
	
	$statistics=$pager->get_statisticsHTML($_SESSION['match_statistics']);
	print( $statistics);
    $pagerHTML=$pager->getPagerHTML($p_page);
	print( $pagerHTML);
    $tmpTable=$pager->get_pageHTML($p_page);
    print($tmpTable);
    print("<br/>");
    print( $pagerHTML);
    print("<a href='GetTab.php?id=".htmlspecialchars(session_id())."' target='_blank'>Get tab-delimited file</a>");
    print("&nbsp;");
     print("<a href='GetTabDarwin.php?id=".htmlspecialchars(session_id())."' target='_blank'>Get tab-delimited file (Darwin import) </a>");
}

function handleCSV($file, $field, $kingdomfield)
{
    $sources=Array();
	$has_headers = false;
    if(array_key_exists("source_gbif", $_REQUEST))
    {
        $sources[]="gbif";
    }
	if(array_key_exists("source_gbif_vernacular", $_REQUEST))
    {
        $sources[]="gbif_vernacular";
    }
    if(array_key_exists("source_worms", $_REQUEST))
    {
        $sources[]="worms";
    }
	 if(array_key_exists("headers", $_REQUEST))
    {
        $has_headers = true;
    }
	
	$languages = Array();
	$languages[] = "nld";
	$languages[] = "fre";
	$languages[] = "fra";
	$languages[] = "deu";
	$languages[] = "eng";
	$myParser= new CSVParser($file, $field, $has_headers, "\t", $kingdomfield, $sources, $languages);
	$myParser->parseFile();
    handleParsedCSV(1);
	unlink($file);
}

if(array_key_exists("results", $_SESSION)===false||array_key_exists("page", $_REQUEST)===false)
{
    $name=$_FILES['file_to_upload']['name'];
    $server_file=NULL;


    $uploaddir = './uploads/';
    $uploadfile = $uploaddir . basename($_FILES['file_to_upload']['name']);



    $hashname=sha1($_FILES['file_to_upload']['tmp_name']);
   
    if (move_uploaded_file($_FILES['file_to_upload']['tmp_name'], $uploaddir."/".$hashname))
	{
        
        $server_file=  $uploaddir."/".$hashname;
        
        if(is_numeric($_REQUEST['pos_data_field']))
        {
            handleCSV($server_file, $_REQUEST['pos_data_field'],  $_REQUEST['pos_kingdom_field']);
			if(file_exists($_FILES['file_to_upload']['tmp_name']))
			{
				unlink($_FILES['file_to_upload']['tmp_name']);
            }
			//$_SESSION["results"];
        }
        else
        {
          print("NOGO");
            
        }
    } else {
        echo "Possible file upload attack!\n";
    }
}
else
{
    handleParsedCSV($_REQUEST['page']);
}
?>

