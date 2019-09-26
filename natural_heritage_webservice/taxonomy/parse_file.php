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
?>


<?php

function handleParsedCSV($p_page)
{
   
    $pager= new HTMLPager($_SESSION[session_id()]["results"], "50", "./parse_file.php?id=".session_id()."&page=", $_SESSION[session_id()]["headers"]);
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

function handleCSV($file, $mail, $field, $kingdomfield)
{
    $sources=Array();
	$has_headers = false;
	if(array_key_exists("source_darwin", $_REQUEST))
    {
        $sources[]="darwin";
    }
    if(array_key_exists("source_gbif", $_REQUEST))
    {
        $sources[]="gbif";
    }
	if(array_key_exists("source_gbif_vernacular", $_REQUEST))
    {
        $sources[]="gbif_vernacular";
    }
	if(array_key_exists("source_iucn", $_REQUEST))
    {
        $sources[]="iucn";
    }
    if(array_key_exists("source_worms", $_REQUEST))
    {
        $sources[]="worms";
    }
	 if(array_key_exists("headers", $_REQUEST))
    {
        $has_headers = true;
    }
	if(array_key_exists("rank_field", $_REQUEST))
    {
        $rank_field = $_REQUEST['rank_field'];
    }
	if(array_key_exists("rank_position_field", $_REQUEST))
    {
        $rank_position_field = $_REQUEST['rank_position_field'];
    }
	
	$languages = Array();
	$languages[] = "nld";
	$languages[] = "fre";
	$languages[] = "fra";
	$languages[] = "deu";
	$languages[] = "eng";
    try
   {   

        $myParser= new CSVParser($file, $mail, $field, $has_headers, "\t", $kingdomfield, $sources, $languages, $rank_field, $rank_position_field );
		//$myParser->startClient();
        $_SESSION[session_id()]["csv_parser"]= $myParser;

        $urlTmp="http://localhost/".preg_replace("/\/([^\/]+)$/","/async_parser.php?id=".session_id(),$_SERVER["REQUEST_URI"]);

        $cmd="nohup curl -X POST --data 'obj=".base64_encode(serialize($myParser))."' --cookie ".session_name() . '=' . session_id()." --silent $urlTmp > /dev/null  & ";

        shell_exec($cmd);

        
        
    }
    catch(Exception $e)
    {
        print($e->getMessage());
    }
    //$myParser->parseFile();
       
    //handleParsedCSV(1);
	//unlink($file);
}
$_SESSION[session_id()]["init"]=true;
if(array_key_exists("id", $_REQUEST))
{
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
elseif(array_key_exists("csv_parser",$_SESSION[session_id()]))
{
        $myParser=$_SESSION[session_id()]["csv_parser"];
        print("resume");
         if(!array_key_exists(["results", $_SESSION[session_id()]]))
        {
            print("display_result");
        }
        handleParsedCSV($_REQUEST['page']);
}
elseif(array_key_exists("results", $_SESSION[session_id()])===false||array_key_exists("page", $_REQUEST)===false)
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
            handleCSV($server_file, $_REQUEST['mail'],  $_REQUEST['pos_data_field'],  $_REQUEST['pos_kingdom_field']);
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
       // echo "Possible file upload attack!\n";
    }
}
else
{
    handleParsedCSV($_REQUEST['page']);
}
?>



<?php if(!array_key_exists("id", $_REQUEST)):?>
<div id="waiting">
waiting...
</div>
Counter specimen : <div id="counter">
</div>
If no data click after a few minutes :
<a href="parse_file.php?id=<?php print(session_id())?>">parse_file.php?id=<?php print(session_id())?></a>
<script language="JavaScript">
        var previous=-1;
        var current=-2;
		var flagRun=true;
		var loopTimeout=function()
		{
            if(current>=0)
            {
                previous=current;
            }
			$.getJSON( "count_data.php",{'id': '<?php print(session_id())?>'},
                function(data)
                {
                    $("#counter").html(data.cpt);
                    current=data.cpt;
                    if(current==previous)
                    {
                        flagRun=false;
                        window.location.href = window.location.href+"?id=<?php print(session_id())?>";
                        
                      
                                   
                    }
                 });					
		}
		$(document).ready(
			function()
			{

				
				
			
				var myTimeout=function () {
					setTimeout(
						function()
						{
							loopTimeout();
							if(flagRun)
							{
								myTimeout();
							}
						},5000)
				}					
				;
				myTimeout();
			}
			

		);


</script>
<?php endif;?>
