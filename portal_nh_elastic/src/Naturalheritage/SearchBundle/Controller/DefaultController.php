<?php

namespace Naturalheritage\SearchBundle\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Bundle\FrameworkBundle\Controller\Controller;

use Naturalheritage\SearchBundle\Entity\ElasticSearch;
use Naturalheritage\SearchBundle\Form\ElasticSearchType;

use ONGR\ElasticsearchDSL\Query\TermLevel\TermQuery;
use ONGR\ElasticsearchDSL\Query\FullText\MatchPhraseQuery;
use ONGR\ElasticsearchDSL\Highlight\Highlight;
use ONGR\ElasticsearchDSL\Aggregation\Bucketing\TermsAggregation;
use ONGR\ElasticsearchDSL\Query\FullText\MultiMatchQuery;
use ONGR\ElasticsearchDSL\Query\Compound\BoolQuery;

use Elasticsearch\ClientBuilder;
use Symfony\Component\HttpFoundation\JsonResponse;

class DefaultController extends Controller
{
    
    private $max_results=10;
    private $client_created=false;
    private $elastic_client=NULL;

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

	return	 $this->render('NaturalheritageSearchBundle:Default:elasticsearch.html.twig');
	
    }

    protected function returnBucket($criteria, $aggregation)
    {
	
	$nested=Array();
        $nested['criteria']=$criteria;
        $nested['details']=Array();
	foreach ($aggregation as $bucket) {
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
	$choices[] = $this->returnBucket('institution', $results->getAggregation('institution'));
	$choices[] = $this->returnBucket('collection', $results->getAggregation('collection'));
	$choices[] = $this->returnBucket('authors', $results->getAggregation('authors'));
	$returned["documents"]=$results;
	$returned["facets"]=$choices;
	$returned["count"]= $results->count();
        $returned['pagination']=$pagination;
 	        
	return $returned;
    }



    protected function doSearch($query_params, $page)
    {
	$resultArray=Array();
	//$jsonQuery=Array();
	$finder = $this->container->get('es.manager.default.document');
	$search = $finder->createSearch();
	foreach($query_params as $key=>$value)
	{
		//$jsonQuery[$key]=$value;
		if($key=="fulltext")
		{
			if(strlen($value)>2)
			{
				$bool = new BoolQuery();
				$termQuery = new MatchPhraseQuery('content_ngrams', $value);
				$termQuery2 = new MatchPhraseQuery('content', $value);
				$bool->add($termQuery, BoolQuery::SHOULD);
				$bool->add($termQuery2, BoolQuery::SHOULD);
				$search->addQuery($bool, BoolQuery::MUST);
			}
		}
		if($key=="institutions")
		{
			$institutions=explode("|",$value);
			$bool = new BoolQuery();
			foreach($institutions as $value)
			{
				$termQuery = new TermQuery('institution', $value);
				$bool->add($termQuery, BoolQuery::SHOULD);
			}
			$search->addQuery($bool, BoolQuery::MUST);				
		}
		if($key=="authors")
		{
			if(strlen($value)>2)
			{
				$authors=explode("|",$value);
				$bool = new BoolQuery();
				foreach($authors as $value)
				{
					$termQuery = new MatchPhraseQuery('authors', $value);
					$termQuery2 = new MatchPhraseQuery('authors.authors_ngram', $value);
					$bool->add($termQuery, BoolQuery::SHOULD);
					$bool->add($termQuery2, BoolQuery::SHOULD);
				}
				$search->addQuery($bool, BoolQuery::MUST);
			}
		}
	}
	

	$termsAggregationInstitution = new TermsAggregation('institution');
	$termsAggregationInstitution->setField('institution');
	$termsAggregationCollection = new TermsAggregation('collection');
	$termsAggregationCollection->setField('bundle_name');
	$termsAggregationAuthors = new TermsAggregation('authors');
	$termsAggregationAuthors->setField('authors');
	$search->addAggregation($termsAggregationInstitution);
	$search->addAggregation($termsAggregationCollection);
	$search->addAggregation($termsAggregationAuthors);
	$search->setSize($this->max_results);
	$search->setFrom($this->max_results*($page-1));
	$results = $finder->findDocuments($search);
	$resultArray=$this->parseElasticResult($results, $page);
		
	return $resultArray;
    }

    public function searchelasticsearchAction()
    {
	return	 $this->render('NaturalheritageSearchBundle:Default:elasticsearch.html.twig');
	
   
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
		return	 $this->render('NaturalheritageSearchBundle:Default:elasticsearch_partial_result.html.twig', array('results'=>$resultArray["documents"], 'facets'=>$resultArray["facets"], 'count'=>$resultArray["count"], 'pagination'=>$resultArray['pagination']));
	}
	else
	{
		return	 $this->render('NaturalheritageSearchBundle:Default:elasticsearch_partial_result.html.twig');
	}

    }


	protected function get_highlights(&$p_returned, $p_highlights, $p_patternregex, $p_key )
	{
		if(array_key_exists($p_key,  $p_highlights ))
		{

			foreach($p_highlights[$p_key] as $value)
			{
			
				$value=strtolower(strip_tags($value));
				$value = preg_replace('/\s+/', ' ',$value);
				$matches=Array();
			
				preg_match($p_patternregex, $value, $matches);
				if(count($matches)>0)
				{	
					$p_returned[]=rtrim($matches[0], ".");
	
				}						
			}
		}	
	}

	public function autocompleteAction($textpattern, $fields, $fields_highlight)
	{
		$this->instantiateClient();
		$client = $this->elastic_client;          
		$params = [
		    'index' => $this->getParameter('elastic_index'),
		    'type' => $this->getParameter('elastic_type'),
		    'body' => [
			'_source'=> $fields,
			'query' => [
			    'multi_match' => [
				'query' => $textpattern,
				'type' => 'phrase',
				'fields'=> $fields
			    ]
			],
			'highlight' => ['fields'    => $fields_highlight,  'fragment_size' => 300]
		    ]
		];
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
		return $this->autocompleteAction($key, ['content', 'content_ngrams'], array('content_ngrams' => new \stdClass(), 'content' => new \stdClass())); 
	}

	public function autocompleteauthorsAction(Request $request)
	{
		 $key = $request->query->get('q');
		return $this->autocompleteAction($key, ['authors', 'authors.authors_ngrams'], array('authors' => new \stdClass(), 'authors.authors_ngrams' => new \stdClass())); 
	}

	public function autocompletefieldallAction( $keywordfield)
	{
		$returned=Array();
		
			$this->instantiateClient();
			$client = $this->elastic_client;          
			$params = [
			    'index' => $this->getParameter('elastic_index'),
			    'type' => $this->getParameter('elastic_type'),
			    'size' => 0,
			    'body' => [
				'_source'=> $keywordfield,
				'aggs' => [
				    'getall' => [
					'terms' => 
						['field' => $keywordfield,
						]
				    ]
				]
			    ]
			];
		
			$results = $client->search($params);
			
		
			$returned=Array();
			$i=0;
			foreach($results["aggregations"]["getall"]["buckets"] as $key=>$doc)
			{				
				$row["id"]=$doc["key"];
				$row["text"]=$doc["key"];
				$returned[]=$row;			
				$i++;
			}
		
		return new JsonResponse($returned);
	}
}
