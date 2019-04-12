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
    
    protected $max_results = 10;
    protected $client_created = false;
    protected $elastic_client = NULL;
    protected $template_index = 'NaturalheritageSearchBundle:Default:elasticsearch.html.twig';
    protected $template_iframe = 'NaturalheritageSearchBundle:Default:elasticsearch_stripped.html.twig';
    protected $template_results= 'NaturalheritageSearchBundle:Default:elasticsearch_partial_result.html.twig';
    protected $template_iframe_search = 'NaturalheritageSearchBundle:Frames:elasticsearch_frame_search.html.twig';
    protected $template_iframe_result = 'NaturalheritageSearchBundle:Frames:elasticsearch_frame_search.html.twig';
    protected $template_iframe_map = 'NaturalheritageSearchBundle:Frames:map.html.twig';
    protected $template_details = 'NaturalheritageSearchBundle:Default:select2_partial_detailed.html.twig';
    protected $frame_modules=false;
    protected $session=null;
    protected $search_map="on";
    protected static $levenshtein_pattern="";
   
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

    public function indexAction()
    {        
        return	 $this->render($this->template_index, array('map'=>$this->search_map));	
    }
    
    public function indexNoMapAction()
    {
       $this->search_map="off";
       return $this->indexAction();
	
    }

    public function indexiframemoduleAction()
    {
       $this->start_nh_session();
        $this->frame_modules=true;
        $this->template_index=$this->template_iframe_search;
        return	 $this->render($this->template_index,array('map'=>$this->search_map));
    }
    
    public function indexmapframemoduleAction()
    {
        $this->start_nh_session();
        return	 $this->render($this->template_iframe_map);
    }
    
    public function indexIFrameAction()
    {
        $this->template_index=$this->template_iframe;
        return $this->indexAction();
    }

    public function indexIFrameNoMapAction()
    {
        $this->search_map="off";        
        return $this->indexIFrameAction();
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

    protected function parseElasticResult($results, $page)
    {
		$returned=Array();
	
		$pagination = array(
            'page' => $page,
            'route' => 'naturalheritage_search_searchelasticsearchpartial',
            'pages_count' => ceil($results->count() / $this->max_results)
        );
		$choices = Array();
		$choices[] = $this->returnBucket('institution', $results->getAggregation('institution'),"#elastic_search_institution");
		$choices[] = $this->returnBucket('Collection', $results->getAggregation('main_collection'), "#elastic_search_collection");
    	$choices[] = $this->returnBucket('Sub-collection', $results->getAggregation('sub_collection'), "#elastic_search_collection");
		$choices[] = $this->returnBucket('Object type', $results->getAggregation('object_type'),"#elastic_search_what");
    	$choices[] = $this->returnBucket('Who', $results->getAggregation('search_criteria_who'), "#elastic_search_who");
    	$choices[] = $this->returnBucket('Country', $results->getAggregation('country'), "#elastic_search_where");
    	$choices[] = $this->returnBucket('Geographical', $results->getAggregation('locality'), "#elastic_search_where");
		$keys=Array();   
		$id=($page-1)*($this->max_results);	
		foreach($results as $doc)
		{
			$keys[$doc->id]=++$id;
			
		}
		$returned["ids"]=$keys;
		$returned["documents"]=$results;
		$returned["facets"]=$choices;
		//$returned['facets_to_search_criteria']=Array();	
		$returned["count"]= $results->count();
		$returned['pagination']=$pagination;
	
		return $returned;
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
        //$boolQuery->add($geoQuery, BoolQuery::FILTER);
        //$p_search->addQuery($boolQuery);
    }
    
    protected function doSearch($query_params, $page)
    {

        $resultArray=Array();
        //$jsonQuery=Array();
        $finder = $this->container->get('es.manager.default.document');
        $search = $finder->createSearch();
        
        $flagHasNumber=$query_params->has("subcriteria_what_object_number");

        foreach($query_params as $main_key=>$query_detail)
        {
            
            if($main_key=="fulltext")
            {
                $value=$query_detail["fulltext"];
                if(strlen($value)>1)
                {
                       $bool = new BoolQuery();
                       $termQuery = new MatchPhraseQuery('content_text', $value);
                       $termQuery2 = new MatchPhraseQuery('content_text.content_text_ngrams', $value);
                       $bool->add($termQuery, BoolQuery::SHOULD);
                       $bool->add($termQuery2, BoolQuery::SHOULD);
                       $search->addQuery($bool, BoolQuery::MUST);
                    
                }
            }
            
            elseif($main_key=="institutions")
            {
                $value=$query_detail["institutions"];
                $institutions=explode("|",$value);
                $bool = new BoolQuery();
                foreach($institutions as $value)
                {
                    $termQuery = new TermQuery('institution', $value);
                    $bool->add($termQuery, BoolQuery::SHOULD);
                }
                $search->addQuery($bool, BoolQuery::MUST);				
            }
           elseif($main_key=="collections")
            {
                //TEMP                
                $value=$query_detail["collections"];
                $collections=explode("|",$value);
                $bool = new BoolQuery();
                $fields=Array("department", "main_collection", "sub_collection");
                
                foreach($collections as $value)
                {
                    foreach($fields as $field)
                    {
                        $termQuery = new TermQuery($field, $value);
                        $bool->add($termQuery, BoolQuery::SHOULD);
                    }
                }
                $search->addQuery($bool, BoolQuery::MUST);				
            }
            elseif(($main_key=="who"||$main_key=="where"||$main_key=="what")&&!$flagHasNumber)
            {
                $boolean="OR";
                if(array_key_exists("boolean", $query_detail))
                {
                    $boolean=$query_detail["boolean"];
                }
                $this->parseSearchCriteria($search, $query_detail, "search_criteria", $main_key, Array('search_criteria.value', 'search_criteria.value.value_ngrams', 'search_criteria.value.value_full' ), Array("search_criteria.main_category"=> $main_key, "search_criteria.sub_category"=>$query_detail["sub_category"] ),"phrase", 'gte',  $boolean);
            }
            /*elseif($main_key=="what")
            {
                $this->parseSearchCriteria($search, $query_detail, "object_identifiers", $main_key, Array('object_identifiers.identifier', 'object_identifiers.identifier.identifier_ngrams', 'object_identifiers.identifier.identifier_full' ), Array("object_identifiers.identifier_type"=> $query_detail["sub_category"] ));
            }*/
            elseif(($main_key=="date_from")&&!$flagHasNumber)
            {
                $this->parseSearchCriteria($search, $query_detail, "dates", $main_key, Array("dates.date_begin" ), Array("dates.date_type"=> $query_detail["sub_category"] ), "range","gte");
            }
            elseif(($main_key=="date_to")&&!$flagHasNumber)
            {
                $this->parseSearchCriteria($search, $query_detail, "dates", $main_key, Array("dates.date_begin" ), Array("dates.date_type"=> $query_detail["sub_category"] ), "range","lte");
            }
             elseif($main_key=="bbox"&&!$flagHasNumber)
             {
                $this->parseBBOX($search, $query_detail["north"], $query_detail["west"], $query_detail["south"], $query_detail["east"] );
             }
             elseif(substr($main_key, 0,12)=="subcriteria_")
             {
                
                //object number has a MUST clause
                if(($flagHasNumber&&$main_key=="subcriteria_what_object_number")||!$flagHasNumber)
                {

                    $main_key=substr($main_key, 12);
                    $parse_criteria=explode("_", $main_key);
                    $main_criteria=array_shift($parse_criteria);
                    $sub_criteria=implode("_", $parse_criteria);
                    $sub_criteria=str_replace("_BLANK_", " ", $sub_criteria);
                    if($main_key=="what_object_number")
                    {

                         $search = $finder->createSearch();
                        $type="term";
                        
                    }
                    else
                    {

                        $type="phrase";
                       
                    }   
                    
                   $boolean="OR";
                    if(array_key_exists("boolean", $query_detail))
                    {
                        $boolean=$query_detail["boolean"];
                    }
                    $this->parseSearchCriteria($search, $query_detail, "search_criteria", "value", Array('search_criteria.value', 'search_criteria.value.value_ngrams', 'search_criteria.value.value_full' ), Array("search_criteria.main_category"=> $main_criteria, "search_criteria.sub_category"=>str_replace("_BLANK_", " ",$query_detail["sub_category"]) ), $type, 'gte',  $boolean,BoolQuery::SHOULD);
                }
             }
				
           
        
        }
	

        $buckets= array("institution", "main_collection", "sub_collection","object_type");
	    foreach($buckets as $bucket)
	    {
		$termsAggregation = new TermsAggregation($bucket);
		$termsAggregation->setField($bucket);
		$search->addAggregation($termsAggregation);
	    }
	    $displayWho=  new TermsAggregation("search_criteria_who_base");
	    $displayWho->setField("search_criteria.value.value_full");
	    $filterWho= new TermQuery('search_criteria.main_category', 'who');
	    $filterAggregationWho = new FilterAggregation('who', $filterWho);
	    $filterAggregationWho->addAggregation($displayWho);    
		$nestedAggregationWho = new NestedAggregation('search_criteria_who', 'search_criteria');
	    $nestedAggregationWho->addAggregation($filterAggregationWho);
	    $search->addAggregation($nestedAggregationWho);
	    
	    $displayCountry=  new TermsAggregation("search_criteria_country_base");
	    $displayCountry->setField("search_criteria.value.value_full");
	    $filterCountry= new TermQuery('search_criteria.sub_category', 'country');
	    $filterAggregationCountry = new FilterAggregation('country', $filterCountry);
	    $filterAggregationCountry->addAggregation($displayCountry);    
		$nestedAggregationCountry = new NestedAggregation('country', 'search_criteria');
	    $nestedAggregationCountry->addAggregation($filterAggregationCountry);
	    $search->addAggregation($nestedAggregationCountry);
	    
	    $displayLocality=  new TermsAggregation("search_criteria_locality_base");
	    $displayLocality->setField("search_criteria.value.value_full");
	    $filterIsWhere= new TermQuery('search_criteria.main_category', 'where');
	    $filterIsNotCountry= new TermQuery('search_criteria.sub_category', 'country');
	    $filterIsNotCountry2= new TermQuery('search_criteria.sub_category', 'Country');
	    $bool = new BoolQuery();
	    $bool->add($filterIsWhere, BoolQuery::MUST);
	    $bool->add($filterIsNotCountry, BoolQuery::MUST_NOT);
	    $bool->add($filterIsNotCountry2, BoolQuery::MUST_NOT);
	    $filterAggregationLocality = new FilterAggregation('locality', $bool);
	    $filterAggregationLocality->addAggregation($displayLocality);    
		$nestedAggregationLocality = new NestedAggregation('locality', 'search_criteria');
	    $nestedAggregationLocality->addAggregation($filterAggregationLocality);
	    $search->addAggregation($nestedAggregationLocality);
    
		$search->setSize($this->max_results);
		$search->setFrom($this->max_results*($page-1));
		$results = $finder->findDocuments($search);
	
   
	
		$resultArray=$this->parseElasticResult($results, $page);
		
        return $resultArray;
    }
	


    public function searchelasticsearchAction()
    {
	return	 $this->render($this->template_index);
	
   
    }
                    

    public function searchelasticsearchforpartialAction(Request $request)
    {

        $page=1;
        if($request->request->has('page'))
        {
            $page=$request->request->get('page');
        }
        $resultArray=$this->doSearch($request->request, $page);
        if(count($resultArray)>0)
        {
            return	 $this->render($this->template_results, array('results'=>$resultArray["documents"], 'facets'=>$resultArray["facets"], 'count'=>$resultArray["count"], 'pagination'=>$resultArray['pagination'], 'ids'=>$resultArray['ids']));
        }
        else
        {
            return	 $this->render($this->template_results);
        }
   

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
             //$this->levenshtein_pattern=$textpattern;
            //usort($returned, array('Naturalheritage\SearchBundle\Controller\DefaultController', 'sort_by_nbwords'));
            
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
			$row["id"]=str_replace(" ", "_BLANK_", $doc["key"]);
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
		
		//$returned=array_unique($returned);
		return new JsonResponse($returned);
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
        print_r($search->toArray());
        
        $results = $finder->findDocuments($search);
        print($object_id);
        print_r($results->count());
        //print_r(foreech $results as $doc);

    }
}
