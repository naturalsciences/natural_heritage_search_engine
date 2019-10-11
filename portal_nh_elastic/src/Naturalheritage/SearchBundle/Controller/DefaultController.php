<?php

namespace Naturalheritage\SearchBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Bundle\FrameworkBundle\Controller\Controller;

use Naturalheritage\SearchBundle\Entity\ElasticSearch;
use Naturalheritage\SearchBundle\Form\ElasticSearchType;

use ONGR\ElasticsearchDSL\Query\TermLevel\TermQuery;
use ONGR\ElasticsearchDSL\Query\TermLevel\TermsQuery;
use ONGR\ElasticsearchDSL\Query\FullText\MatchPhraseQuery;
use ONGR\ElasticsearchDSL\Query\FullText\MatchPhrasePrefixQuery;
use ONGR\ElasticsearchDSL\Highlight\Highlight;
use ONGR\ElasticsearchDSL\Aggregation\Bucketing\TermsAggregation;
use ONGR\ElasticsearchDSL\Aggregation\Bucketing\FilterAggregation;
use ONGR\ElasticsearchDSL\Aggregation\Bucketing\NestedAggregation;
use ONGR\ElasticsearchDSL\Query\FullText\MultiMatchQuery;
use ONGR\ElasticsearchDSL\Query\Compound\BoolQuery;
use ONGR\ElasticsearchDSL\Query\Joining\NestedQuery;
use ONGR\ElasticsearchDSL\Query\TermLevel\RangeQuery;
use ONGR\ElasticsearchDSL\Query\MatchAllQuery;
use ONGR\ElasticsearchDSL\Query\Geo\GeoBoundingBoxQuery;
use ONGR\ElasticsearchDSL\Aggregation\Pipeline\BucketScriptAggregation;


use Elasticsearch\ClientBuilder;
use Symfony\Component\HttpFoundation\JsonResponse;

use Symfony\Component\HttpFoundation\Session\Session;

class DefaultController extends Controller
{
    
	
    protected $max_results = 12;
    protected $size_agg = 10;
    protected $client_created = false;
    protected $elastic_client = NULL;

    #2019 08 26
    protected $template_index_facets = 'NaturalheritageSearchBundle:Default:elasticsearch_facets.html.twig';
    protected $template_result_facets = 'NaturalheritageSearchBundle:Default:elasticsearch_result_facets.html.twig';
    protected $template_detail_facets = 'NaturalheritageSearchBundle:Default:elasticsearch_detail_facets.html.twig';
    protected $template_index = 'NaturalheritageSearchBundle:Standalone:elasticsearch.html.twig';
    protected $template_result = 'NaturalheritageSearchBundle:Standalone:elasticsearch_result.html.twig';
    protected $template_detail = 'NaturalheritageSearchBundle:Standalone:elasticsearch_detail.html.twig';
    

    protected $template_details = 'NaturalheritageSearchBundle:Default:select2_partial_detailed.html.twig';
    protected $frame_modules=false;
    protected $session=null;
    protected $search_map="on";
    protected static $levenshtein_pattern="";
    protected $expanded="false";
   
    protected function recursiveFind(array $array, $needle)
    {
        $iterator  = new \RecursiveArrayIterator($array);
        $recursive = new \RecursiveIteratorIterator(
            $iterator,
            \RecursiveIteratorIterator::SELF_FIRST
        );
        foreach ($recursive as $key => $value) {
            if ($key === $needle) {
                return $value;
            }
        }
    }
    
    protected function start_nh_session()
    {
        if($this->session===NULL)
        {
            $this->session = new Session();
            $this->session->start();
        }
    }
    
    protected function instantiateClient()
    {
	
        if(!isset($this->elastic_client))
        {
            $hosts = [$this->getParameter('elastic_server_for_api')	];
            $clientBuilder = ClientBuilder::create();   // Instantiate a new ClientBuilder
            $clientBuilder->setHosts($hosts);           // Set the hosts
            $this->elastic_client = $clientBuilder->build();          // Build the client object
        }
    }
    
    public function indexNoMapAction()
    {
       $this->search_map="off";
       return $this->indexAction();
	
    }

    protected function returnBucket($criteria, $aggregation, $jquery_control)
    {
	
        $nested=Array();
        $nested['criteria']=$criteria;
        $nested['details']=Array();
        $nested['jquery_control']=$jquery_control;
      
        $buckets=$this->recursiveFind((array)$aggregation, "buckets");
        
        foreach ($buckets as $bucket) {
            $tmp=Array();
            $tmp["value"]=$bucket['key'];
            $tmp["count"]=$bucket['doc_count'];
            $nested['details'][]=$tmp; 
           }
        return $nested;
    }

    

        
    protected function parseSearchCriteria(&$p_search, $p_query_detail, $p_base_field, $p_main_key, $p_array_value_fields, $p_array_category_fields, $p_type="phrase", $p_range_term="gte", $p_boolean="OR", $p_default_boolean=BoolQuery::SHOULD)
    {
         
         $value=$p_query_detail[$p_main_key];
      
	$text_pattern=explode("|",$value);
	if(strlen($value)>2)
	{
		$textpatterns=explode("|",$value);
        	if(strtoupper($p_boolean)=="AND")
		{
			foreach($textpatterns as $value)
			{
				$bool2 = new BoolQuery();
		        	foreach($p_array_value_fields as $field)
		        	{
                    
                            
                            if($p_type=="range")
		            		{
		                		$rangeQuery = new RangeQuery($field,[$p_range_term=> $value]);
		                		$bool2->add($rangeQuery,$p_default_boolean);                        
		            
		            		}
                            elseif($p_type=="prefix")
		            		{
		                		$prefixQuery = new MatchPhrasePrefixQuery($field, $value);
		                		$bool2->add($prefixQuery, $p_default_boolean);
		            		}
		            		elseif($p_type=="phrase")
		            		{
		                		$termQuery = new MatchPhraseQuery($field, $value);
		                		$bool2->add($termQuery, $p_default_boolean);
		            		}
                            elseif($p_type=="term")
		            		{
                           
		                		$termQuery = new TermQuery($field, $value);
		                		$bool2->add($termQuery,$p_default_boolean);
		            		}
		           		  
		        	}
				$nested2 =  new NestedQuery($p_base_field, $bool2);
				
				$p_search->addQuery($nested2, BoolQuery::MUST);
			}
            	}
		else
		{
			 $bool = new BoolQuery();
			foreach($textpatterns as $value)
			{
				foreach($p_array_value_fields as $field)
				{
				    if($p_type=="phrase")
				    {
				        $termQuery = new MatchPhraseQuery($field, $value);
				        $bool->add($termQuery, $p_default_boolean);
				    }
                    elseif($p_type=="prefix")
				    {
				        $rangeQuery = new MatchPhrasePrefixQuery($field,$value);
				        $bool->add($rangeQuery, $p_default_boolean);                        
				    
				    }
				    elseif($p_type=="range")
				    {
				        $rangeQuery = new RangeQuery($field,[$p_range_term=> $value]);
				        $bool->add($rangeQuery, $p_default_boolean);                        
				    
				    }
                    elseif($p_type=="term")
		           {                  
		                $termQuery = new TermQuery($field, $value);
		                $bool->add($termQuery, $p_default_boolean);
		           }
				}
			}
            		$nested =  new NestedQuery($p_base_field, $bool);
			$p_search->addQuery($nested, BoolQuery::MUST);
		}
		foreach($p_array_category_fields as $key=>$value)
		{
		        if($value !="*")
		        {
		            $termQueryCategory = new TermQuery($key, $value);
		            $nested2 =  new NestedQuery($p_base_field, $termQueryCategory);
		            $p_search->addQuery($nested2, BoolQuery::MUST);
		        }
		    }
		}			
    }

    protected function parseBBOX(&$p_search, $p_north, $p_west, $p_south, $p_east)
    {
        $location = [
            ['lat' => $p_north, 'lon' => $p_west],
            [ 'lat' => $p_south, 'lon' => $p_east],
        ];

        $boolQuery = new BoolQuery();
        $boolQuery->add(new MatchAllQuery());
        $geoQuery = new GeoBoundingBoxQuery('coordinates.geo_ref_point', $location);
        $nested =  new NestedQuery("coordinates", $geoQuery);
        $p_search->addQuery($nested, BoolQuery::MUST);
    }
    	


    public function searchelasticsearchAction()
    {
        return	 $this->render($this->template_index);	   
    }

	protected function get_highlights(&$p_returned, $p_highlights, $p_patternregex, $p_key, $regex=true, $remove_extra=false, $init_cap=false )
	{
		if(array_key_exists($p_key,  $p_highlights ))
		{

			foreach($p_highlights[$p_key] as $value)
			{
			
				$value=strtolower(strip_tags($value));
                if($remove_extra)
                {
                    $value = preg_replace('/\;/', ' ',$value);
                    $value = preg_replace('/\./', ' ',$value);
                    $value = preg_replace('/\:/', ' ',$value);
				}
                if($init_cap)
                {
                    $value=ucwords($value);
                }
                $value = preg_replace('/\s+/', ' ',$value);
				
                if(strlen($p_patternregex)>0)
                {
                    $matches=Array();
                    preg_match($p_patternregex, $value, $matches);
                    if(count($matches)>0)
                    {	
                        $p_returned[]=rtrim($matches[0], ".");
        
                    }
				}
                else
                {
                    $p_returned[]=rtrim($value, ".");
                }
                						
			}
		}	
	}

    
    private static function sort_by_nbwords($aw, $bw)
    {
        $a= str_word_count($aw);
        $b= str_word_count($bw);
        if ($a == $b) {
            return ($aw < $bw) ? -1 : 1;
        }
        return ($a < $b) ? -1 : 1;
    }  
    
        private static function sort_by_levenshtein($aw, $bw)
    {
           $a= levenshtein($aw, $this->levenshtein_pattern);
           $b= levenshtein_pattern($bw, $this->levenshtein_pattern);
            if ($a == $b) {
                return ($aw < $bw) ? -1 : 1;
            }
            return ($a < $b) ? -1 : 1;
    }  
    

    public function autocompletekeywordAction($textpattern, $filters_cond, $nested_path, $fields, $fields_highlight)
    {
            $finder = $this->container->get('es.manager.default.document');
            $search = $finder->createSearch();
           
            $this->parseSearchCriteria($search, ["pattern"=> $textpattern], "search_criteria", "pattern", Array('search_criteria.value', 'search_criteria.value.value_ngrams', 'search_criteria.value.value_full' ), $filters_cond , "prefix");

            $displayCriteria=  new TermsAggregation("search_criteria_base");
            $displayCriteria->setField("search_criteria.value.value_full");
            
            
            $bool = new BoolQuery();
            if(array_key_exists('search_criteria.sub_category', $filters_cond))
            {
                $filterCriteria1= new TermQuery('search_criteria.sub_category', $filters_cond['search_criteria.sub_category']);
                $bool->add($filterCriteria1, BoolQuery::MUST);
            }
            $filterCriteria2= new TermQuery('search_criteria.main_category', $filters_cond['search_criteria.main_category']);
            $bool->add($filterCriteria2, BoolQuery::MUST);
            $filterAggregationCriteria = new FilterAggregation('criteria', $bool);
            $filterAggregationCriteria->addAggregation($displayCriteria);    
            $nestedAggregationCriteria = new NestedAggregation('criteria', 'search_criteria');
            $nestedAggregationCriteria->addAggregation($filterAggregationCriteria);
            $search->addAggregation($nestedAggregationCriteria);
            $search->setSize(1);
            
            
            $results = $finder->findDocuments($search);
            
            $choices = Array();
            $choices[] = $this->returnBucket('criteria', $results->getAggregation('criteria'),"");
            $returned=Array();
            $json_array=Array();
            foreach($choices as $choice);            
            {
               
                 foreach($choice['details'] as $tmp)
                 {
                    $returned[]=$tmp['value'];
                    
                 }
            }
            
			$sort_data=Array();
            foreach($returned as $key=>$value) 
            {
				$sort_data[$value]=$this->pos_and_levenshtein(strtolower($value), strtolower($textpattern));
            }
			
			array_multisort($sort_data, SORT_ASC, $returned);
			array_unshift($returned, $textpattern);
            $returned=array_unique($returned);
            foreach($returned as $value)
            {
                $row["id"]=$value;
                $row["text"]=$value;
                $json_array[]=$row;			
                
            }
            return new JsonResponse($json_array);   

            
        
    }
	
	public function pos_and_levenshtein($a, $b)
	{
		$tmp=strpos($a, $b);
		if($tmp===FALSE)
		{
			return 15+	levenshtein(substr($a,0,strlen($b)), $b);		
		}
		else
		{			
			return $tmp;
		}
	
	}
    
   
    
	public function autocompleteAction($textpattern, $fields, $fields_highlight, $in_all=false)
	{
		$this->instantiateClient();
		$client = $this->elastic_client;          
		if(!$in_all)
        {           
            $params = [
                'index' => $this->getParameter('elastic_index'),
                'type' => $this->getParameter('elastic_type'),
                'body' => [
                '_source'=> $fields,
                'query' => [
                    'multi_match' => [
                    'query' => $textpattern,
                    'type' => 'phrase_prefix',
                    'fields'=> $fields
                    ]
                ],
                'highlight' => ['fields'    => $fields_highlight,  'fragment_size' => 300]
                ]
            ];            
        }
        else
        {
            $params = [
                'index' => $this->getParameter('elastic_index'),
                'type' => $this->getParameter('elastic_type'),
                'body' => [
                'query' => [
                        'match_phrase' => [
                            $fields[0]=> $textpattern
                            ]
                    ],
                     'highlight' => ['fields'    => $fields_highlight,  'fragment_size' => 300]
                  ]
            ];
        }
		$patternregex = '/\b'.$textpattern.'[^\s]*?\b.*?(\.|$)/i';
		$results = $client->search($params);
		
		
		$returned=Array();
        
		foreach($results["hits"]["hits"] as $key=>$doc)
		{				
			foreach($fields as $single_field)
			{
				$this->get_highlights($returned, $doc["highlight"], $patternregex, $single_field);
			}
		}
		$i=1;
		$json_array=Array();
		sort($returned);
		array_unshift($returned, $textpattern);
		$returned=array_unique($returned);
		foreach($returned as $value)
		{
			$row["id"]=$value;
			$row["text"]=$value;
			$json_array[]=$row;			
			$i++;
		}
		return new JsonResponse($json_array);
	}

	public function autocompletefulltextAction(Request $request)
	{
		 $key = $request->query->get('q');
		return $this->autocompleteAction($key, ['content_text', 'content_text.content_text_ngrams'], array('content_text' => new \stdClass(), 'content_text.content_text_ngrams' => new \stdClass()));
              
	}

    protected function autocompletekeywordsAction($key, $array_filters )
	{
    
		 
		return $this->autocompletekeywordAction($key, $array_filters, "search_criteria", ['search_criteria.value','search_criteria.value.value_ngrams','search_criteria.value.value_full'], array('search_criteria.value' => new \stdClass(),'search_criteria.value.value_ngrams' => new \stdClass(),'search_criteria.value.value_full' => new \stdClass())); 
	}
    
	
    public function autocompletewhatAction(Request $request)
	{
		 $key = $request->query->get('q');
		$filter_array= Array( "search_criteria.main_category" => "what");
		
        if($request->query->has('criteria'))
		{
        
			if(strlen($request->query->get('criteria'))>0)
			{
             
				$filter_array["search_criteria.sub_category"]=$request->query->get('criteria');
			}
		}
       
		return $this->autocompletekeywordsAction($key, $filter_array); 
	}
    
    
    public function autocompletewhoAction(Request $request)
	{
		 $key = $request->query->get('q');
		$filter_array= Array( "search_criteria.main_category" => "who");
		if($request->query->has('criteria'))
		{
			if(strlen($request->query->get('criteria'))>0)
			{
				$filter_array["search_criteria.sub_category"]=$request->query->get('criteria');
			}
		}
		return $this->autocompletekeywordsAction($key, $filter_array); 
	}
    
    public function autocompletewhereAction(Request $request)
	{
		 $key = $request->query->get('q');
		$filter_array= Array( "search_criteria.main_category" => "where");
		if($request->query->has('criteria'))
		{
			if(strlen($request->query->get('criteria'))>0)
			{
				$filter_array["search_criteria.sub_category"]=str_replace('_BLANK_',' ',$request->query->get('criteria'));
			}
		}
		return $this->autocompletekeywordsAction($key, $filter_array); 
	}
    
    


	public function autocompletefieldall_nested($parent, $keywordfield, $filtercriteria, $second_agg=null, $sort_criteria="sorting_weight")
	{
		$returned=Array();
        $tmp_agg['terms']= [ "field" => $keywordfield];
        if(!is_null($second_agg))
        {
       
            $tmp_agg["aggs"]=$second_agg;
		}
        $this->instantiateClient();
		$client = $this->elastic_client;          
		$params = [
		        'index' => $this->getParameter('elastic_index'),
		        'type' => $this->getParameter('elastic_type'),
		        'size' => 0,
		        'body' => [
		       
		            "aggs" => [
		                        $parent => [
		                        "nested" => [ "path"=> $parent]
		                         ,
		                        "aggs" => [
		                              "filtercriteria" =>
		                                   [
	
							"filter" => $filtercriteria,
		                                       "aggs"=> 
                                                [
		                                                  "getall" => $tmp_agg
		                                              ]
		                                  ]  
						
		                              ]
		                                  
		                        ]
		                      ]
		          ]
                 ];
		
		$results = $client->search($params);
		
		
			
		$i=0;
        $tmpArray=$results["aggregations"][$parent]["filtercriteria"]["getall"]["buckets"];
        if(!is_null($second_agg))
        {
            $sort_data=Array();
            foreach($tmpArray as $key=>$value) 
            {
               $sort_idx=Array();
               foreach($value['sorting_weight']['buckets']  as $tmp_sort);
               {
                    $sort_idx[]=$tmp_sort['key'];
                    
               }         
                $sort_data[$key]=max($sort_idx);
            }
            
            array_multisort($sort_data, SORT_DESC, $tmpArray);
        }
		foreach( $tmpArray as $key=>$doc)
		{				
			$row["id"]=$doc["key"];//str_replace(" ", "_BLANK_", $doc["key"]);
			$row["text"]=str_replace(" ", "_BLANK_", $doc["key"]);
			$returned[]=$row;			
			$i++;
		}
		if(is_null($second_agg))
        {
            sort($returned);
		}
        return $returned;
        }    
        

	public function autocompletefieldallAction(Request $request, $keywordfield)
	{
		$filter=[
		                'match_all'=>(object)[]
		                ];
		$extra_filter=[];
	       
		if($keywordfield=="institution")
		{
		    $keywordfields=Array("institution");
		}
		elseif($keywordfield=="collection")
		{
		     if($request->query->has('institutions'))
		     {
		        //$extra_filter.=$request->query->get('institutions');
		        $tmp=$request->query->get('institutions');
		        $build_query=explode('|',$tmp);
		       
		        $extra_filter=["terms"=>["institution"=>$build_query]];//["bool"=>["must"=>["terms"=>["institution"=>$build_query]]]];
		        
		     }
		    $keywordfields=Array("department", "main_collection", "sub_collection");
		}
		elseif($keywordfield=="who"||$keywordfield=="where")
		{
			$extra_filter= ["term"=> ["search_criteria.main_category"=>$keywordfield]];
			
			
			$tmp= $this->autocompletefieldall_nested("search_criteria", "search_criteria.sub_category", $extra_filter );
			return new JsonResponse($tmp);
		}
        elseif($keywordfield=="what")
		{
			$extra_filter= ["term"=> ["search_criteria.main_category"=>$keywordfield]];
			
			
			$tmp= $this->autocompletefieldall_nested("search_criteria", "search_criteria.sub_category", $extra_filter , $second_agg);
			return new JsonResponse($tmp);
		}
        
        
		else
		{
			$keywordfields=Array($keywordfield);
		}
		$returned=Array();
		foreach($keywordfields as $keywordfield_value)
		{
			$this->instantiateClient();
			$client = $this->elastic_client;
			    if(count($extra_filter)>0)
			    {
				$filter=$extra_filter;
			    }
			$params = [
			    'index' => $this->getParameter('elastic_index'),
			    'type' => $this->getParameter('elastic_type'),
			    'size' => 0,
			    'body' => [
				'_source'=> $keywordfield_value,
				'aggs' => [
                 
				    'getall' => [
                    			'filter'=> $filter,
					'aggs'=>['nh_terms'=>['terms' => 
						['field' => $keywordfield_value,
						]]]
 
				    ]
				]
			    ]
			];
		
			$results = $client->search($params);
			
		
			
			$i=0;
			
			foreach($results["aggregations"]["getall"]['nh_terms']["buckets"] as $key=>$doc)
			{				
				$row["id"]=$doc["key"];
				$row["text"]=$doc["key"];
				$returned[]=$row;			
				$i++;
			}
        	}
		sort($returned);
		
		return new JsonResponse($returned);
	}

	
    
    public function cetafRDFRouteAction($institution, $collection_string, $object_id, $sub_criteria="object_number", $format_field="format_of_document", $format_value="Web page", $object_type_field="main_object_category", $object_type_value="Zoological specimen" )
    {
        $finder = $this->container->get('es.manager.default.document');
        $search = $finder->createSearch();      


       $search->addQuery(new TermQuery('institution', $institution), BoolQuery::MUST); 


        $bool = new BoolQuery();
        $fields=Array("department", "main_collection", "sub_collection");
        foreach($fields as $field)
        {
            $termQuery = new TermQuery($field, $collection_string);
            $bool->add($termQuery, BoolQuery::SHOULD);                    
        }
        $search->addQuery($bool, BoolQuery::MUST);	

      
       $this->parseSearchCriteria(
            $search,  
            Array( "value" => $object_id, "sub_category" => "object_number", "boolean" => "OR" ), 
            "search_criteria", 
            "value",
             Array('search_criteria.value', 'search_criteria.value.value_ngrams', 'search_criteria.value.value_full' ), 
            Array("search_criteria.main_category"=> "what", "search_criteria.sub_category"=>"object_number" ), 
           
            "term", 'gte', "AND",BoolQuery::MUST);

        $results = $finder->findDocuments($search);
    }
	
	// FACET DEV 2019 (keep autocomplte from above)
    
    public function indexAction_logic(Request $request, $template)
    {
        $map=$request->get("map",'off');
        $details=$request->get("details",'off');
        $session = $request->getSession(); 
		$session->remove('es_result');		
		$session->remove('expanded');
	    $session->remove('extra_params');
		$session->remove('extra_params2');
		$session->remove('extra_params_generic');
	    $session->remove('extra_params_facets');
		$session->remove('extra_params2_facets');
        $session->remove("state_history");
        $session->set("state_history", Array());        
	
        return	 $this->render($template, array("map"=> $map, "details"=>$details));
        //return	 $this->render($this->template_index_facets, array("map"=> $map, "details"=>$details));
            
    }
    
    public function indexFacetsAction(Request $request)
    {
         return $this->indexAction_logic($request, $this->template_index_facets);
    }
    
    public function indexAction(Request $request)
    {
         return $this->indexAction_logic($request, $this->template_index);
    }
    
     public function resultAction_logic(Request $request, $template)
    {        
          $session = $request->getSession();
          $data=$session->get("es_result",false);
		  $page =  $request->get("page",1);
          if($data!==false)
          { 
			$pagination = array(
            'page' => $page,
            'route' => 'naturalheritage_search_searchelasticsearchpartial',
            'pages_count' => ceil($data["hits"]["total"] / $this->max_results)
			);
            return	 $this->render($template, array("data"=> $data["hits"], "pagination"=> $pagination, "page_size"=> $this->max_results));
          }
    }
    
    
    public function resultFacetsAction(Request $request)
    {        
            return $this->resultAction_logic($request, $this->template_result_facets);
    }
    
    
    public function resultAction(Request $request)
    {        
            return $this->resultAction_logic($request, $this->template_result);
    }
	
	public function detailAction_logic(Request $request, $template)
    {
		
		$session = $request->getSession();
          $data=$session->get("es_result",false);
          $agg=$request->get("agg", "what");
          if($data!==false)
          { 
            return	 $this->render($this->template_detail_facets, array("data"=> $data["aggregations"]));
          }
	}

    public function detailFacetsAction(Request $request)
    {
            return	 $this->detailAction_logic($request, $this->template_detail_facets);
    }	

    public function detailAction(Request $request)
    {
            return	 $this->detailAction_logic($request, $this->template_detail);
    }	
    

   
     protected function es_wrapper_logic($session, $p_term,$p_extra_params, $p_extra_params_annex, $p_extra_params_generic, $p_extra_params_facets, $p_extra_params_annex_facets, $p_coordinates,  $p_date_from, $p_date_from_types, $p_date_to, $p_date_to_types , $p_page, $p_expanded)
    {

            $go_query=false;
            $results=Array();
		    
			if(strtolower($p_expanded=="true"))
			{

				$session->set("expanded","true");
			}
			else
			{
				$session->set("expanded","false");
			}
            //$term = $request->query->get('term',"");
            
            $this->instantiateClient();
			$client = $this->elastic_client;
            $page=$p_page;
            $term=$p_term;
			$from= ($page -1 ) * $this->max_results; 
          
            if(isset($p_extra_params)||isset($p_extra_params_generic)||isset($p_coordinates)||isset($p_date_from)||isset($p_date_to))
            {
                $extra_params=Array();
				$extra_params_facets=Array();
				$extra_params2=Array();
				$extra_params2_facets=Array();
                $extra_params_generic=Array();
                $coordinates=Array();
				$date_from="";
				$date_from_types=Array();
				$date_to="";
				$date_to_types=Array();
                if(isset($p_extra_params))
                {
                    $extra_params = json_decode($p_extra_params,true);
					
					$session->set("extra_params", $extra_params);
                }
				if(isset($p_extra_params_facets))
                {
                    $extra_params_facets = json_decode($p_extra_params_facets,true);
					
					$session->set("extra_params_facets", $extra_params_facets);
                }
				if(isset($p_extra_params_generic))
                {				
                    $extra_params_generic = json_decode($p_extra_params_generic,true);
					
					$session->set("extra_params_generic", $extra_params_generic);
                }
				 if(isset($p_extra_params_annex))
                {
                    $extra_params2 = json_decode($p_extra_params_annex,true);
					$session->set("extra_params2", $extra_params2);
                }
				if(isset($p_extra_params_annex_facets))
                {
                    $extra_params2_facets = json_decode($p_extra_params_annex_facets,true);
					$session->set("extra_params2_facets", $extra_params2_facets);
                }
                if(isset($p_coordinates))
                {
                    $coordinates = explode(";",urldecode($p_coordinates));
					
                }
				if(isset($p_date_from))
                {					
                    $date_from=$p_date_from;
					$date_from_types = explode("|",urldecode($p_date_from_types));
                }
				if(isset($p_date_to))
                {					
                    $date_to=$p_date_to;
					$date_to_types = explode("|",urldecode($p_date_to_types));
                }

				
				//FULL TEXT
                $criteriasDirect=Array();
				$criteriasMain=Array();
				if(strlen($term)>1)
				{
                    $array_term = preg_split("/(:| |;|,|\!|\?|<&)/", $term );
                    if(count($array_term)>1)
                    {
                        $criteriasMain=[                                        
                                            'common' => [
                                                'content_text' => 
                                                ["query"=> $term,									
                                                "minimum_should_match"=> count($array_term)-1,
                                                 "cutoff_frequency"=> 0.001,
                                                "low_freq_operator"=>"and",
                                              
                                               
                                                ]
                                            ]
                                        
                                   
                                ];
                   }
                   else
                   {
                         $criteriasMain=[
                                                'multi_match' => [
                                                     'query'=> $term,
                                                    "fields"=> ['content_text.content_text_ngrams', 'content_text'],
                                                    
                                                    ] 
                                                                                                
                                   
                                ];
                   }
				}
				//FACETS
                $clauses=Array();
                $clausesNested=Array();
				$clausesNestedFacets=Array();
                $criteriaBuildNested=Array();
				$criteriaBuildNestedFacets=Array();
			    $criteriaBuild2=Array();
                $operatorsClausesNested=Array();
                $operatorsClauses2=Array();
				foreach($extra_params as $criteria )
                {
                       if(array_key_exists("operator",$criteria))
                       {
                            $operatorsClausesNested[$criteria["field"]]=$criteria["operator"];
					   }
                       $clausesNested[$criteria["field"]][]=[
										"bool" =>
											[
												"must" => [
													["bool"=>
														[
															"should"=>
															[
																["term" => [ "search_criteria.value.value_full" => $criteria["term"]]],
																["term" => [ "search_criteria.value" => $criteria["term"]]]
															]
														]],
													 ["term" => [ "search_criteria.sub_category" => $criteria["field"]]]
											],
										   
								]];
                }
				foreach($extra_params_facets as $criteria )
                {

                       $clausesNestedFacets[$criteria["field"]][]=[
										"bool" =>
											[
												"must" => [
													["bool"=>
														[
															"should"=>
															[
																["term" => [ "search_criteria.value.value_full" => $criteria["term"]]],
																["term" => [ "search_criteria.value" => $criteria["term"]]]
															]
														]],
													 ["term" => [ "search_criteria.sub_category" => $criteria["field"]]]
											],
										   
								]];
                }
				foreach($extra_params_generic as $criteria )
                {
                    
                       if(array_key_exists("operator",$criteria))
                       {
                            $operatorsClausesNested[$criteria["field"]]=$criteria["operator"];
					   }
					   $clausesNested[$criteria["field"]][]=[
										"bool" =>
											[
												"must" => [
														["bool"=>
														[
															"should"=>
															[
																["term" => [ "search_criteria.value.value_full" => $criteria["term"]]],
																["term" => [ "search_criteria.value" => $criteria["term"]]]
															]
														]],
													 ["term" => [ "search_criteria.main_category" => $criteria["field"]]]
											],
										   
								]];
                }				
				if(count($clausesNested)>0)
				{
					foreach($clausesNested as $concept => $sub_query)
					{
                        $boolean="should";
                        if(array_key_exists($concept,$operatorsClausesNested))
                        {
                            if(strtolower($operatorsClausesNested[$concept]=="and"))
                            {                            
                                $boolean="must";
                            }
                        }
						if($boolean=="must")
                        {
                            
                            
                            foreach($sub_query as $must_query)
                            {
                               
                                $criteriaBuildNested[] =[ 
                                "nested" => [
                                    "path" => "search_criteria",
                                    "query" => [
                                        "bool" =>
                                            [
                                                 $boolean => 
                                                    $must_query
                                                
                                            ]
                                        ]
                                   ]
                            ];
                            }
                            
                        }
                        else
                        {
                            $criteriaBuildNested[$concept] =[ 
                                "nested" => [
                                    "path" => "search_criteria",
                                    "query" => [
                                        "bool" =>
                                            [
                                                 $boolean => [
                                                    $sub_query
                                                ]
                                            ]
                                        ]
                                   ]
                            ];
                        }
                    }
				}
				
				if(count($clausesNestedFacets)>0)
				{
					foreach($clausesNestedFacets as $concept => $sub_query)
					{
          
                            $criteriaBuildNestedFacets[$concept] =[ 
                                "nested" => [
                                    "path" => "search_criteria",
                                    "query" => [
                                        "bool" =>
                                            [
                                                 "should" => [
                                                    $sub_query
                                                ]
                                            ]
                                        ]
                                   ]
                            ];
                        
                    }
				}
				if(count($extra_params2)>0)
                {
                    $clausesTmp=Array();
                    foreach($extra_params2 as $criteria )
                    {
                         $boolean="should";
                        if(array_key_exists("operator",$criteria))
                        {
                                if(strtolower($criteria["operator"]=="and"))
                                {
                                     $boolean="must";
                                }
                               
                        }
                        if(strtolower($criteria["field"])=="all_collections")
                        {
                            $operatorsClauses2[$criteria["field"]]=$boolean;
                            $clausesTmp[$criteria["field"]][]=
                                    [
                                        "bool"=>
                                            [
                                                "should"=>
                                                    [
                                                        ["term"=> ["main_collection" => $criteria["term"]] ],
                                                        ["term"=> ["sub_collection" => $criteria["term"]] ]
                                                    ]
                                            ]
                                    ];
                        }
                        else
                        {
                            $operatorsClauses2[$criteria["field"]]=$boolean;
                            $clausesTmp[$criteria["field"]][]=["term"=> [$criteria["field"] => $criteria["term"]] ];                        
                        }
                    }
                    
                    foreach($clausesTmp as $key=>$sub_array)
                    {
                            $clauses[]=[
                                            "bool"=>
                                            [
                                                $operatorsClauses2[$key]=>$sub_array
                                            ]
                                        ];
                    }
				}
                
				if(count($extra_params2_facets)>0)
                {
                    $clausesTmp=Array();
                    foreach($extra_params2_facets as $criteria )
                    {
                        
                         $clausesTmp[$criteria["field"]][]=["term"=> [$criteria["field"] => $criteria["term"]] ];                        
                        
                    }
                    
                    foreach($clausesTmp as $key=>$sub_array)
                    {
                            $clauses[]=[
                                            "bool"=>
                                            [
                                                "should"=>$sub_array
                                            ]
                                        ];
                    }
				}
                
				
				//COORD
				$clausesCoordinates=Array();
				$criteriaGeo=Array();
				$has_geo = false;
                
				if(count($coordinates)==4)
				{
					$west=$coordinates[0];
					$east=$coordinates[1];
					$south=$coordinates[2];
					$north=$coordinates[3];
					$has_geo=true;
				}
                if($has_geo===true)
				{
				
					$clausesCoordinates[]=[
											
													"geo_bounding_box"=>
														[
															"coordinates.geo_ref_point" =>
																[
																	"top_left"=> 
																		[
																			"lat"=> $north,
																			"lon"=> $west
																		],
																	"bottom_right"=> 
																		[
																			"lat"=> $south,
																			"lon"=> $east
																		]	
																]
														]
												
										];
					$criteriaGeo =[ 
                        "nested" => [
                            "path" => "coordinates",
                            "query" => [
                                "bool" =>
                                    [
                                        "should" => [
                                            $clausesCoordinates
                                        ]
                                    ]
                                ]
                           ]
                    ];
				}
				
				//DateFrom
				$clausesDateFrom=Array();
				if(strlen($date_from)>0)
				{
					$buildDateFrom=Array();
					$buildDateFrom[]=[
                                        "range" =>
                                            [
                                                 "dates.date_begin" => [
                                                    "gte"=>$date_from
                                                ]
                                            ]
                                        ];
					if(count($date_from_types)>0&&!in_array("all",array_map('strtolower',$date_from_types)))
					{
						if(count($date_from_types)==1)
						{
								$buildDateFrom[]=[
                                        "term" =>
                                             [
												"dates.date_type" => $date_from_types[0]
											]
                                            
                                        ];
						}
						else
						{
							$tmpBooleanDate=Array();
							foreach($date_from_types as $type)
							{
								$tmpBooleanDate[]=[
                                        "term" =>
                                             [
												"dates.date_type" => $date_from_types[0]
											]
                                            
                                        ];
							}
							$buildDateFrom[]=[
											"bool"=>
												[
													"should"=>$tmpBooleanDate
												]
										];
						}
					}
					$clauses[]=[ 
                         "nested" => [
                                    "path" => "dates",
                                    "query" => [
										 "bool" =>
											[
												"must" => [
													$buildDateFrom
												]
											]
										]
                                   ]
                            ];
				}
				
				$clausesDateTo=Array();
				if(strlen($date_to)>0)
				{
					$buildDateTo=Array();
					$buildDateTo[]=[
										"bool"=>
											[
												"should"=>
												[
													"range" =>
														[
															 "dates.date_begin" => [
																"lte"=>$date_to
															]
														]
													,
													"range" =>
														[
															 "dates.date_end" => [
																"lte"=>$date_to
															]
														]
												]
											]
                                        ];
					if(count($date_to_types)>0&&!in_array("all",array_map('strtolower',$date_to_types)))
					{
						if(count($date_to_types)==1)
						{
								$buildDateTo[]=[
                                        "term" =>
                                             [
												"dates.date_type" => $date_to_types[0]
											]
                                            
                                        ];
						}
						else
						{
							$tmpBooleanDate=Array();
							foreach($date_to_types as $type)
							{
								$tmpBooleanDate[]=[
                                        "term" =>
                                             [
												"dates.date_type" => $date_to_types[0]
											]
                                            
                                        ];
							}
							$buildDateTo[]=[
											"bool"=>
												[
													"should"=>$tmpBooleanDate
												]
										];
						}
					}
					$clauses[]=[ 
                         "nested" => [
                                    "path" => "dates",
                                    "query" => [
										 "bool" =>
											[
												"must" => [
													$buildDateTo
												]
											]
										]
                                   ]
                            ];
				}
				
				$allCriterias=Array();
                
                $array_criteria= Array();

				if(count($criteriaBuildNested)>0)
				{
					foreach($criteriaBuildNested as $sub_criteria=>$sub_query)
					{
						$array_criteria["must"][]=$sub_query;
					}
				}
				
				if(count($criteriaBuildNestedFacets)>0)
				{
					foreach($criteriaBuildNestedFacets as $sub_criteria=>$sub_query)
					{
						$array_criteria["must"][]=$sub_query;
					}
				}
	
				if(count($clauses)>0)
				{
					foreach($clauses as $sub_criteria=>$sub_query)
					{
						$array_criteria["must"][]=$sub_query;
					}
				}
                
				if(count($criteriaGeo)>0)
				{
					 $array_criteria["must"][]=$criteriaGeo;
				}
				if(count($criteriasMain)>0)
				{
					 $array_criteria["must"][]=$criteriasMain;
				}

                
                  $queryParam=[
                        "bool"=>
                            $array_criteria
                       
                    ];
               
               
               $go_query=true; 
            }
            elseif(strlen($term)>1)
            {     
                    $array_term = preg_split("/(:| |;|,|\!|\?|<&)/", $term );
                    if(count($array_term)>1)
                    {
                        $queryParam=[                                        
                                            'common' => [
                                                'content_text' => 
                                                ["query"=> $term,									
                                                "minimum_should_match"=> count($array_term)-1,
                                                 "cutoff_frequency"=> 0.001,
                                                "low_freq_operator"=>"and"           
                                               ]
                                            ]
                                        
                                   
                                ];
                   }
                   else
                   {
                         $queryParam=[
                                                'multi_match' => [
                                                     'query'=> $term,
                                                    "fields"=> ['content_text.content_text_ngrams', 'content_text']
                                                    ] 
                                                                                                
                                   
                                ];
                   }                        
                  $go_query=true;                         
			}
			if($go_query)
            {
                $params = [
                    'index' => $this->getParameter('elastic_index'),
                    'type' => $this->getParameter('elastic_type'),
                    'from' => $from,
                    'size' => $this->max_results,
                    'body' => [
                         'query' => $queryParam,
                             "aggs" =>[
                                "institution" => [
                                                 "terms" => [ 
                                                            "field" =>  "institution"  
                                                             , "size"=> $this->size_agg
                                                            ]
                                                  ,"aggs"=> [
                                                    "department"=>
                                                        [
                                                        "terms"=>[
                                                               "field"=>"department"
                                                               , "size"=> $this->size_agg
                                                               ],
                                                               "aggs" => 
                                                               [
                                                                "collection"=> [
                                                                    "terms"=> 
                                                                        [
                                                                            "field"=>"main_collection"
                                                                                , "size"=> $this->size_agg
                                                                        ],
                                                                        "aggs" => 
                                                                           [
                                                                            "sub_collection"=> [
                                                                                "terms"=> 
                                                                                    [
                                                                                        "field"=>"sub_collection"
                                                                                            , "size"=> $this->size_agg
                                                                                    ]
                                                                                     
                                                                                ]
                                                                                
                                                                           ]
                                                                         
                                                                    ]
                                                                    
                                                               ]
                                                        ]
                                                  ]                      
                                                ],
                                "main_agg" => [
                                    "nested" => [
                                        "path" => "search_criteria"
                                    ],
                                    "aggs" => [
                                        "where" => [
                                           
                                            "filter" => [ "term" => [  "search_criteria.main_category" => "where"  ] ],
                                            "aggs" => [
                                                "agg_result" => [ 
                                                    "terms" => [ 
                                                            "field" =>  "search_criteria.sub_category"  
                                                             , "size"=> $this->size_agg
                                                            ] 
                                                       ,
                                                       "aggs"=> [
                                                      
                                                            "agg_value"=> [
                                                                "terms" => [ 
                                                                    "field" =>  "search_criteria.value.value_full"  
                                                                     , "size"=> $this->size_agg
                                                                    ] 
                                                            ]
                                                       ]
                                                    ]
                                            ]
                                        ],
                                        "what" => [
                                           
                                            "filter" => [ "term" => [  "search_criteria.main_category" => "what"  ] ],
                                            "aggs" => [
                                                "agg_result" => [ 
                                                    "terms" => [ 
                                                            "field" =>  "search_criteria.sub_category"  
                                                             , "size"=> $this->size_agg
                                                            ] 
                                                       ,
                                                       "aggs"=> [
                                                      
                                                            "agg_value"=> [
                                                                "terms" => [ 
                                                                    "field" =>  "search_criteria.value.value_full"  
                                                                     , "size"=> $this->size_agg
                                                                    ] 
                                                            ]
                                                       ]
                                                    ]
                                            ]
                                        ],
                                        "who" => [
                                           
                                            "filter" => [ "term" => [  "search_criteria.main_category" => "who"  ] ],
                                            "aggs" => [
                                                "agg_result" => [ 
                                                    "terms" => [ 
                                                            "field" =>  "search_criteria.sub_category"  
                                                             , "size"=> $this->size_agg
                                                            ] 
                                                       ,
                                                       "aggs"=> [
                                                      
                                                            "agg_value"=> [
                                                                "terms" => [ 
                                                                    "field" =>  "search_criteria.value.value_full"  
                                                                     , "size"=> $this->size_agg
                                                                    ] 
                                                            ]
                                                       ]
                                                    ]
                                            ]
                                        ]
                                    ]
                                ]
                            ]
                    ]
                ];
            
                $results = $client->search($params);
                $session->set("es_result", $results);
           }           
           return new JsonResponse($results);
       }
         
    protected function recordStateHistory($request, $session)
    {
        $history=$session->get("state_history", Array());
        $newHistory=Array();
        if($request->query->has('term'))
        {
            $newHistory["term"]=$request->query->get('term');            
        }
        if($request->query->has('extra_params'))
        {
            $newHistory["extra_params"]=$request->query->get('extra_params');            
        }
        if($request->query->has('extra_params_annex'))
        {
            $newHistory["extra_params_annex"]=$request->query->get('extra_params_annex');            
        }
        if($request->query->has('coordinates'))
        {
            $newHistory["coordinates"]=$request->query->get('coordinates');            
        }
        if($request->query->has('extra_params_generic'))
        {
            $newHistory["extra_params_generic"]=$request->query->get('extra_params_generic');            
        }
        if($request->query->has('extra_params2'))
        {
            $newHistory["extra_params2"]=$request->query->get('extra_params2');            
        }
        if($request->query->has('extra_params_facets'))
        {
            $newHistory["extra_params_facets"]=$request->query->get('extra_params_facets');            
        }
        if($request->query->has('extra_params_annex_facets'))
        {
            $newHistory["extra_params_annex_facets"]=$request->query->get('extra_params_annex_facets');            
        }
        if($request->query->has('date_from'))
        {
            $newHistory["date_from"]=$request->query->get('date_from');            
        }
         if($request->query->has('date_from_type'))
        {
            $newHistory["date_from_type"]=$request->query->get('date_from_type', "all");            
        }
         if($request->query->has('date_to'))
        {
            $newHistory["date_to"]=$request->query->get('date_to');            
        }
        if($request->query->has('date_to_type'))
        {
            $newHistory["date_to_type"]=$request->query->get('date_to_type',"all");            
        }
        if($request->query->has('page'))
        {
            $newHistory["page"]=$request->query->get('page',1);            
        }
        if($request->query->has('expanded'))
        {
            $newHistory["expanded"]=$request->query->get('expanded',"false");            
        }
         $history[]=$newHistory;
         $session->set("state_history", $history);
        
        
    }
    
    public function backAction(Request $request)
    {
        $session = $request->getSession();
        $history=$session->get("state_history", Array());
        if(count($history)>=1)
        {

            $last_state=array_pop($history);
            
            $history=$session->set("state_history", $history);
            return new JsonResponse($last_state);

            
        }
        else
        {
           $response=Array();
            return new JsonResponse($response);
        }
        
    }
    
    public function esWrapperAction(Request $request)
    {
        $session = $request->getSession();
        if($request->query->has('term')||$request->query->has('extra_params')||$request->query->has('extra_params_annex')||$request->query->has('coordinates')||$request->query->has('extra_params_generic')||$request->query->has('date_from')||$request->query->has('date_to'))
		{
            $this->recordStateHistory($request, $session);
            return $this->es_wrapper_logic( 
                $session,
                $request->query->get('term',""), 
                $request->query->get('extra_params'), 
                $request->query->get('extra_params_annex'), 
                $request->query->get('extra_params_generic'),
                $request->query->get('extra_params_facets'), 
                $request->query->get('extra_params_annex_facets'),
                $request->query->get('coordinates'), 
                $request->query->get('date_from'),                  
                $request->query->get('date_from_type',"all"),
                $request->query->get('date_to'),   
                $request->query->get('date_to_type',"all"),
                $request->query->get('page',1),
                $request->get("expanded","false"));
        }
    }
           
	
	public function fancyTreeWrapperAction(Request $request)
    {
		return $this->fancyTreeWrapperActionLogic($request,$request->get('agg', 'what') );
	}
    
    
	protected function multiKeyExists(array $arr, $key) 
	{
		
		// is in base array?
		if (array_key_exists($key, $arr)) {
			return $arr[$key];
		}

		// check arrays contained in this array
		foreach ($arr as $element) {
			if (is_array($element)) {
				if ($this->multiKeyExists($element, $key)) {
					return $element[$key];
				}
			}

		}

		return false;
	}
	
     protected function fancyTreeWrapperActionLogicRawCollection($data, $path_title=Array(), $path_value=Array(), $extra_params=Array())
    {          

          if($data!==false)
          { 
             
			 $source2Tmp=Array();
			 			 
            if(count($path_title)==0)
            {
                $children="\"children\" :[]";
				 
            }
            elseif(count($path_title)>0)
            {
                $dataRecurs=true;
                $current_title=array_shift($path_title);
                $current_value=array_shift($path_value);
                $buckets= $data[$current_title]["buckets"];
                $nestedJsonTmp=Array();
                $count=count($buckets);
                foreach($buckets as $item)
                {   
					$found=false;
                    $title=$item["key"];//. " (".$item["doc_count"].")";
                    $key=htmlspecialchars(str_replace(array("\n", "\t", "\r")," ",$item["key"]));
					
					 foreach($extra_params as $item3)
					 {

							if($item3["field"]==$current_value&&$item3["term"]==$item["key"])
							{								
								$found=true;
												
							}
					}
					if($found)
					{
						$keep_state=",\"selected_on_load\":true";
					}
					else
					{
						$keep_state="";
					}
                    if(count($path_title)>0)
                    {
                        //recursive
                        $recurs=$this->fancyTreeWrapperActionLogicRawCollection($item,  $path_title, $path_value, $extra_params);
                        $recursStr="[".implode(",",$recurs)."]";
                        if(count($recurs)>0)
                        {
							
                            $nestedJsonTmp[]="{\"key\":\"".$key."\"".$keep_state.",\"title\" : \"".htmlspecialchars(str_replace(   array("\n", "\t", "\r"), " ",$title))."\", \"expanded\": ".$this->expanded.", \"children\" : [{\"key\":\"".$path_value[0]."\",\"title\" : \"".
							htmlspecialchars(str_replace(   array("\n", "\t", "\r"), " ", $path_title[0]))." (".count($recurs).")\", \"unselect\":true,\"checkbox\" :true,\"expanded\": ".$this->expanded.", \"children\" :".$recursStr."}]}";
                         }
                         else
                         {
							$title.= " (".$item["doc_count"].")";
                            $nestedJsonTmp[]="{\"key\":\"".$key."\",\"title\" : \"".htmlspecialchars(str_replace(   array("\n", "\t", "\r"), " ",$title))."\", \"expanded\": ".$this->expanded.$keep_state."}";
                         }
                    }
                    else
                    {
						//$title.= " (".$item["doc_count"].")";
                        $nestedJsonTmp[]="{\"key\":\"".$key."\",\"title\" : \"".htmlspecialchars(str_replace(   array("\n", "\t", "\r"), " ",$title))."\", \"expanded\": ".$this->expanded.$keep_state."}";
                    }
                         
                }
         
                   
             }
              if(count( $nestedJsonTmp)>0) 
              {
                $buildString=$nestedJsonTmp;//"[".implode(",", $nestedJsonTmp)."]";
              }
              else
              {
                $buildString=Array();
              }
              return $buildString;
          }
         
    }
    
    public function fancyTreeWrapperActionLogicRaw( $name_agg, $data, $extra_params)
    {         
          if($data!==false)
          { 
             $buckets=$data["aggregations"]["main_agg"][$name_agg]["agg_result"]["buckets"];
			 $source2Tmp=Array();
			 foreach($buckets as $item)
			 {
				 $title=$item["key"];//. " (".$item["doc_count"].")";
                 $key=htmlspecialchars(str_replace(array("\n", "\t", "\r")," ",$item["key"]));
				 $buckets2= $item["agg_value"]["buckets"];
				 $nestedJson3Tmp=Array();
				 foreach($buckets2 as $item2)
				 {
				      $found=false;
					  $title2=$item2["key"]. " (".$item2["doc_count"].")";
                      $key2=htmlspecialchars(str_replace(array("\n", "\t", "\r")," ",$item2["key"]));
					 
					  $parent_exists=array_search($key, array_column($extra_params, "field"));
					  
				      $value_exists= false;
					  if($parent_exists!==false)
					  {
						
						
                        foreach($extra_params as $item3)
					    {
						
							if($item3["field"]==$key&&$item3["term"]==$key2)
							{								
								$found=true;
							}
						}
					  }
					  if($found)
					  {
						$nestedJson3Tmp[]="{\"key\":\"".$key2."\",\"title\" : \"".htmlspecialchars(str_replace(array("\n", "\t", "\r"), " ",$title2))."\", \"expanded\": ".$this->expanded.", \"selected_on_load\":true}";
					  }
					  else
					  {
						$nestedJson3Tmp[]="{\"key\":\"".$key2."\",\"title\" : \"".htmlspecialchars(str_replace(array("\n", "\t", "\r"), " ",$title2))."\", \"expanded\": ".$this->expanded."}";
					   }
				 }
				 $nestedJson3=implode(",", $nestedJson3Tmp);
				 $children2="\"children\" : [".$nestedJson3."]";
				 $source2Tmp[] = "{ \"key\":\"".$key."\",\"title\" :\"".htmlspecialchars(str_replace(array("\n", "\t", "\r"), " ",$title))."\", \"expanded\": ".$this->expanded.", ".$children2." }";
			 }
			  $buildString="[".implode(",", $source2Tmp)."]";
              return $buildString;
          }
          return "";
    }
    
    public function fancyTreeWrapperActionLogic(Request $request, $name_agg)
    {
         $buildString = $this->fancyTreeWrapperActionLogicRaw( $request, $name_agg);
         $response = new JsonResponse();
		 $response = JsonResponse::fromJsonString($buildString);
         return $response;	        
    }
    
    public function fancyTreeWrapperAllAction(Request $request)
    {
        $buildString="";
        $buildArray=Array();
        $session = $request->getSession(); 
		$extra_params=array_merge($session->get("extra_params", Array()),$session->get("extra_params_facets", Array()));
		$extra_params2=array_merge($session->get("extra_params2", Array()),$session->get("extra_params2_facets", Array()));
		
        $data=$session->get("es_result",false);
		$this->expanded = $session->get("expanded","false");

        $institutionArray=$this->fancyTreeWrapperActionLogicRawCollection($data["aggregations"], array("institution", "department", "collection", "sub_collection"), array("institution", "department", "main_collection", "sub_collection"),$extra_params2);        
         if(count($institutionArray)>0)
        {
            $institution="[".implode(",",$institutionArray )."]";
            $buildArray[]="{ \"key\":\"institution\",\"checkbox\" :true,\"title\" :\"Institution (".count($institutionArray).")\", \"expanded\": ".$this->expanded.",\"unselect\":true, \"children\" :".$institution." }";        
            
        }
        
        $what=$this->fancyTreeWrapperActionLogicRaw( "what", $data, $extra_params);
       
        if(strlen($what)>0)
        {
            $buildArray[]="{ \"key\":\"what\",\"title\" :\"what\", \"expanded\": ".$this->expanded.", \"children\" :".$what." }";        
            
        }
        $where=$this->fancyTreeWrapperActionLogicRaw( "where", $data, $extra_params);
        if(strlen($where)>0)
        {
           $buildArray[]="{ \"key\":\"where\",\"title\" :\"where\", \"expanded\": ".$this->expanded.", \"children\" :".$where." }";       
        } 
       $who=$this->fancyTreeWrapperActionLogicRaw( "who", $data, $extra_params);
        if(strlen($who)>0)
        {
           $buildArray[]="{ \"key\":\"who\",\"title\" :\"who\", \"expanded\": ".$this->expanded.", \"children\" :".$who." }";       
        }

       if(count($buildArray)>0)
       {
  
            $buildString="[".implode(",",$buildArray)."]";            
       }       
       $response = new JsonResponse();
	   $response=JsonResponse::fromJsonString(str_replace("\\","\\\\", $buildString));
       return $response;

	}
	
	public function getSearchCriteriaDetailsAction($keywordfield)
        {
		$extra_filter= ["term"=> ["search_criteria.main_category"=>$keywordfield]];
        $second_agg=NULL;
        if($keywordfield=="what")
        {
            $second_agg=["sorting_weight" => ["terms" =>[ "field" => "search_criteria.sub_category_weight"] ]];
		}
        $subCriterias= $this->autocompletefieldall_nested("search_criteria", "search_criteria.sub_category", $extra_filter, $second_agg );
        
		return	 $this->render($this->template_details, array("keywordfield"=> $keywordfield, "subcriterias"=> $subCriterias));
	}
	
	public function dateTypesAction(Request $request)
	{
		 $session = $request->getSession();
		$results=Array();
		if(count($results)==0)
		{
			$this->instantiateClient();
			$client = $this->elastic_client;
			
			$params = [
			    'index' => $this->getParameter('elastic_index'),
			    'type' => $this->getParameter('elastic_type'),
                'size' => 0,
			    'body' => [
                     
                         "aggs" =>[
							"main_agg"=> [
										"nested"=>[
												"path"=>"dates",
												
										
											],
											"aggs"=>
											
												["date_types"=>
													[
														"terms"=>["field"=> "dates.date_type"]
													]
												]
								]
						 ]
						 ]
			];
			$resultsTmp = $client->search($params);
			
			foreach($resultsTmp["aggregations"]["main_agg"]["date_types"]["buckets"] as $tmp)
			{
				
				$val["id"]=$tmp["key"];
				$val["text"]=$tmp["key"];
				$results[]=$val;
			}
			
		}
		return new JsonResponse(array_merge(Array(Array("id"=>"all","text"=>"All")), $results));
		
	}    
    
}
