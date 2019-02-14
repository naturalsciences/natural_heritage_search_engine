<?php

namespace Naturalheritage\OaipmhBundle;

use Symfony\Component\HttpKernel\Bundle\Bundle;
use Naoned\OaiPmhServerBundle\DataProvider\DataProviderInterface;
use Naoned\OaiPmhServerBundle\DependencyInjection\NaonedOaiPmhServerExtension;
use Symfony\Component\DependencyInjection\ContainerAwareTrait;


use Elasticsearch\ClientBuilder;

class NaturalheritageOaipmhBundle  extends Bundle implements DataProviderInterface
{

	protected $client_created = false;
    protected $elastic_client = NULL;
	
	protected function instantiateClient()
    {
	
        if(!isset($this->elastic_client))
        {
            $hosts = [$this->container->getParameter('elastic_server_for_api')	];
            $clientBuilder = ClientBuilder::create();   // Instantiate a new ClientBuilder
            $clientBuilder->setHosts($hosts);           // Set the hosts
            $this->elastic_client = $clientBuilder->build();          // Build the client object
        }
    }
	


        /**
     * @return string Repository name
     */
    public function getRepositoryName()
    {
        return 'TEST OAI-PMH Server NaturalHeritage (BELSPO Project)';
    }

    /**
     * @return string Repository admin email
     */
    public function getAdminEmail()
    {
        return 'franck.theeten@africamuseum.be';
    }

    /**
     * @return \DateTime|string     Repository earliest update change on data
     */
    public function getEarliestDatestamp()
    {
        $returned="";
		$val;
		$this->instantiateClient();
		$params = [
                'index' => $this->container->getParameter('elastic_index'),
                'type' => $this->container->getParameter('elastic_type'),
                'body' => [
						"aggs" => [
							"min_date" => [
                                "filter" => [ "term"=> [ "object_type" => $this->container->getParameter('elastic_oai_type') ] ],
                                "aggs"=>
                                    [
                                        "min_date_value" => 
                                            ["min" => [ "field" => "data_modification_date"]]
                                        
                                    ]
                                ]
                            ]
                        ,
                        'size' => 0
                        ]
                ];
		$results = $this->elastic_client->search($params);
      
		$returned= $results['aggregations']["min_date"]["min_date_value"]["value_as_string"];
		
		return $returned;
    }

	
	protected function map_record($data, $identifier)
	{
		$title="";
		$id="";
		$metadata_date="";
		$creation_date="";
		$url=$identifier;
		$creators = Array();
		$publishers=Array();
		$content=Array();
		$sets = Array();
		$result=$data;
		foreach($result['object_identifiers'] as $key=>$sub_array)
		{
			if($sub_array['identifier_type']=="title")
			{
				$title=$sub_array['identifier'];
				$id=$identifier;
				$found=true;				
			}
			if($sub_array['identifier_type']=="source")
			{
				$publishers[]=$sub_array['identifier'];				
			}
		}
		foreach($result['search_criteria'] as $key=>$sub_array)
		{
			if($sub_array['sub_category']=="author")
			{
				$creators[]=$sub_array['value'];
				
			}
		}
		foreach($result['content_text'] as $key=>$text)
		{
			$content_text[]=$text;
		}
		$sets[]=$result["main_collection"];
		$sets[]=$result["department"];
		$url=$result["url"];
		$metadata_date=$result["data_modification_date"];
		$creation_date=$result["data_creation_date"];
		$creators=array_unique($creators);
		sort($creators);
		$publishers=array_unique($publishers);
		sort($publishers);
		return array(
	            'identifier'  => $identifier,
				'source'  => Array($identifier,$url ),
                'title'       => $title,
				'creator' => $creators,
                'description' => implode(" ", $content_text),
                'last_change' => $metadata_date,
				'creation_date' => $creation_date,
				'publishers' => $publishers,
                'sets'        => $sets
        );
	}
	
    /**
     * @param  string $identifier [description]
     * @return array
     */
    public function getRecord($identifier)
    {
       
		$found=false;
		$returned=Array();
		
		$criteria= str_ireplace($this->container->getParameter("elastic_oai_prefix"),'', $identifier);
		
		$this->instantiateClient();
		$params = [
                'index' => $this->container->getParameter('elastic_index'),
                'type' => $this->container->getParameter('elastic_type'),
                'id' => 'http://'.$criteria
				
            ];
		$result = $this->elastic_client->get($params);
		
		return $this->map_record($result["_source"], $identifier);		
		
    }

    /**
     * must return an array of arrays with keys «identifier» and «name»
     * @return array List of all sets, with identifier and name
     */
    public function getSets()
    {
		$returned=Array();
		$this->instantiateClient();
		$params = [
                'index' => $this->container->getParameter('elastic_index'),
                'type' => $this->container->getParameter('elastic_type'),
                'body' => [
						"aggs" => [
							"article_source" => [
								"filter" => [ "term"=> [ "object_type" => $this->container->getParameter('elastic_oai_type') ] ],
								"aggs" => [
									"institution" => [
										"terms" => [ "field" => "institution" ]
										,
											"aggs"=> [
											"main_collection" => [
												"terms" => [ "field" => "main_collection" ]
											]
										]
									]
								]
							]
						]
                    ,
                     'size' => 0
                  ]
            ];
		$results = $this->elastic_client->search($params);
		foreach($results['aggregations']["article_source"]["institution"]["buckets"] as $key=>$sub_array)
		{
			$institution= $sub_array["key"];
			foreach($sub_array["main_collection"]["buckets"] as $key2=>$sub_array2)
			{
				$name_collection=$sub_array2["key"];
				$returned[]=array(
					'identifier' => $name_collection,
					'name'       => $institution." : ".$name_collection,
					);
			}
			
		}

		return $returned;
		
    }

    /**
     * Search for records
     * @param  String|null    $setTitle Title of wanted set
     * @param  \DateTime|null $from     Date of last change «from»
     * @param  \DataTime|null $until    Date of last change «until»
     * @return array|ArrayObject        List of items
     */
    public function getRecords($setTitle = null, \DateTime $from = null, \DateTime $until = null)
    {
		$returned=Array();
		
		$oaiPmhRuler = $this->container->get('naoned.oaipmh.ruler');
		$this->instantiateClient();
		if(array_key_exists("resumptionToken", $_REQUEST))
		{
            $flag_scroll_es = $oaiPmhRuler->mapToElasticSearchToken($_REQUEST["resumptionToken"], $this->container->get('naoned.oaipmh.cache'));           
			$results = $this->elastic_client->scroll([
            "scroll_id" =>$flag_scroll_es, 
            "scroll" => "120s"           
				]
			);
			
			
		}
		else
		{
            $array_query=Array();
            $array_query[]=	[ 
                                "term"=> [ "object_type" => $this->container->getParameter('elastic_oai_type') ] 
							];
            if(isset($from)||isset($until))
            {
                $default_from="1900-01-01";
                $default_to=date("Y-m-d", time() + 86400);
                if(isset($from))
                {
                    $default_from=$from->format('Y-m-d');
                }
                 if(isset($until))
                {
                    $default_to=$until->format('Y-m-d');
                }
              
                $array_query[]=	[ 
                                "range"=> [ "data_modification_date" => [ "gte"=>  $default_from, "lte"=> $default_to] ] 
							];
            }
            if(isset($setTitle))
            {
                 $array_query[]=["term"=> [ "main_collection" => $setTitle ]] ;
            }
			$params = [
					'index' => $this->container->getParameter('elastic_index'),
					'type' => $this->container->getParameter('elastic_type'),
					'body' => [
								'query'=>[
										'bool' =>  
                                            ["must" => $array_query]
											
									]
								],
				   'size'=>$this->container->getParameter('naoned.oaipmh_server.count_per_load'),
				   'scroll' => '120s'
					
				];
				$results = $this->elastic_client->search($params);
		}
		
		$scroll_id= $results["_scroll_id"];
        
		
		$results=$results["hits"];
		$size=$results["total"];
		$oaiPmhRuler->setTotal($size);
		$oaiPmhRuler->setElasticResumption($scroll_id);
		foreach($results["hits"] as $key=>$sub_array)
		{
			//print_r($sub_array);
			$record_array=$this->map_record($sub_array["_source"], $sub_array["_id"]);
			
			$returned[]=$record_array;
			
		}
		
		return $returned;
  
    }

    /**
     * Tell me, this «record», in which «set» is it ?
     * @param  any   $record An item of elements furnished by getRecords method
     * @return array         List of sets, the record belong to
     */
    public function getSetsForRecord($record)
    {
        return $record['sets'];
    }

	public function getThumb()
	{
		
		return null;
	}
	
    /**
     * Transform the provided record in an array with Dublin Core, «dc_title»  style
     * @param  any   $record An item of elements furnished by getRecords method
     * @return array         Dublin core data
     */
    public  function dublinizeRecord($record)
    {
        return array(
            'dc_identifier'  => $record['source'],
            'dc_title'       => $record['title'],
            'dc_description' => $record['description'],
			'dc_creator' => $record['creator'],
			'dc_publisher' => $record['publishers'],
			'dc_date' => $record['creation_date'],
        );
    }

    /**
     * Check if sets are supported by data provider
     * @return boolean check
     */
    public function checkSupportSets()
    {
        return true;
    }

    /**
     * Get identifier of id
     * @param  any   $record An item of elements furnished by getRecords method
     * @return string        Record Id
     */
    public static function getRecordId($record)
    {
        return $record['identifier'];
    }

    /**
     * Get last change date
     * @param  any   $record An item of elements furnished by getRecords method
     * @return \DateTime|string     Record last change
     */
    public static function getRecordUpdated($record)
    {
        return $record['last_change'];
    }
}
