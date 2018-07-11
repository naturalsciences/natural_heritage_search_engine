<?php
use Elasticsearch\ClientBuilder;
require_once('../resources/vendor/autoload.php');
require_once("csv_parser.php");


$output="/var/developments/output_darwin_worms/elasticsearch_gbif_vernacular_names.txt";

$sources=Array();
$sources[]="gbif";
$languages=Array();
$languages[] = "nld";
$languages[] = "fre";
$languages[] = "fra";
$languages[] = "deu";
$languages[] = "eng";

//ES
$hosts = [

    'http://localhost:9200',       
  
];
$client = ClientBuilder::create()->setHosts($hosts)->build();
 
 $json='{
"size" :0,
  "aggs" : {
    "scientific_name": {
        "nested" :
            {
                "path": "search_criteria"               
            },
            "aggs" :
            {
                "list_taxon" :
                 {
                    "filter" : { "term": { "search_criteria.sub_category": "biological_scientific_name" 
                    } 
                    
                    
                    },
                    "aggs" :
                    { 
                        "output":
                        {
                            "terms" :
                            {
                                "field" : "search_criteria.value.value_full",
                                "size" : 10000000
                            }
                        }
                    }
                  }
            }
    }
    
  }
}';

$params = [
    'index' => 'naturalheritage',
    
    'body' => $json
];

$rs = $client->search($params);
$result=Array();
foreach($rs["aggregations"]["scientific_name"]["list_taxon"]["output"]["buckets"]  as $key=>$record)
{

    //print($record["key"]);
    $result[]=array("taxon"=>$record["key"]);
}


$outputfile = fopen($output, "w");
		
$myParser= new CSVParser(null, "taxon", false, "\t", null, $sources, $languages);
		
$myParser->parseExternalArray($result, "taxon", $outputfile);
$parsed_data =$_SESSION["results"];
fclose($outputfile);

?>