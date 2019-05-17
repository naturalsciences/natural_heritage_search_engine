<?php
//ini_set('display_errors', 1);
//ini_set('display_startup_errors', 1);
//error_reporting(E_ERROR);
require_once("csv_parser.php");
require_once("pager.php");
require_once("get_data_db.php");
header('Content-Type: text/html; charset=utf-8');
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");
?>
 <script src="../js/jquery-3.4.1.min.js"></script> 
<style>
 <?php include 'css/style.css'; ?> 
</style>
<style>
 body {
    font-size: 14px;
 }
</style>

<?php
if(array_key_exists("id", $_REQUEST))
{
	session_id($_REQUEST["id"]);
	session_start();
}
else
{
	session_start();
	session_regenerate_id();
}

function handleParsedCSV($p_page)
{
	
    $pager= new HTMLPager($_SESSION[session_id()]["results"], "50", "./view_data.php?id=".session_id()."&page=", $_SESSION[session_id()]["headers"]);
    print("PAGE = ". $p_page." ");
    print("NB_PAGES = ".  $pager->getNbPages() );
    $pager->get_page($p_page);
	
	$statistics=$pager->get_statisticsHTML($_SESSION[session_id()]['match_statistics']);
	print( $statistics);
    $pagerHTML=$pager->getPagerHTML($p_page);
	print( $pagerHTML);
    $tmpTable=$pager->get_pageHTML($p_page);
    print($tmpTable);
    print("<br/>");
    print( $pagerHTML);
    print("<a href='GetTab.php?id=".htmlspecialchars(session_id())."' target='_blank'>Get tab-delimited file</a>");
    //print("&nbsp;");
     //print("<a href='GetTabDarwin.php?id=".htmlspecialchars(session_id())."' target='_blank'>Get tab-delimited file (Darwin import) </a>");
}
if(array_key_exists("id", $_REQUEST))
{
	//print("get old data");

	$db_parser=new GetDataDB();
	$db_parser->getData($_REQUEST['id']);

	if(array_key_exists("page", $_REQUEST))
	{
		$page=$_REQUEST["page"];
	}
	else
	{
		$page=1;
	}
	handleParsedCSV($page);
	
}
?>
