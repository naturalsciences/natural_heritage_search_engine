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
    
    public function indexAction()
    {
        //return $this->render('NaturalheritageSearchBundle:Default:index.html.twig');
	$elasticSearch = new ElasticSearch();
	$request=$this->getRequest();

	$form = $this->createForm(new ElasticSearchType, $elasticSearch, array('csrf_protection'=>false));
	$form->bind($request);
	if($form->isValid())
	{
		//return $this->render('NaturalheritageSearchBundle:Default:solrsearch.html.twig', array('SolrSearch'=>$solrSearch));
		return	 $this->render('NaturalheritageSearchBundle:Default:elasticsearch.html.twig', array('form'=>$form->createView()));
	}
	else
	{
		$errMsg=(string)$form->getErrors(true, false);
		$validityIssue=$form->getErrorsAsString();
		return $this->render('NaturalheritageSearchBundle:Default:error.html.twig', array("errorMsg"=>$errMsg, "validityIssue"=>$validityIssue));
	}    
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

    protected function parseElasticResult($results)
    {
	$returned=Array();
	
	// Build a list of available choices
	$choices = Array();

	
	
	$choices[] = $this->returnBucket('institution', $results->getAggregation('institution'));
	$choices[] = $this->returnBucket('collection', $results->getAggregation('collection'));
	$returned["documents"]=$results;
	$returned["facets"]=$choices;
	return $returned;
    }

    public function searchelasticsearchAction($textpattern)
    {
	$request=$this->getRequest();
	$elasticSearch = new ElasticSearch();
	$form = $this->createForm(new ElasticSearchType, $elasticSearch, array('csrf_protection'=>false));
	$form->bind($request);
	
	
	
	if($form->isValid())
	{
		if(strlen($textpattern)>2)
		{
			//try{	
			$textpattern=strtolower($textpattern);		
			$finder = $this->container->get('es.manager.default.document');
			$search = $finder->createSearch();

			$termQuery = new MatchPhraseQuery('content_ngrams', $textpattern);
			$termQuery2 = new MatchPhraseQuery('content', $textpattern);			
			$termsAggregationInstitution = new TermsAggregation('institution');
			$termsAggregationInstitution->setField('institution');
			$termsAggregationCollection = new TermsAggregation('collection');
			$termsAggregationCollection->setField('bundle_name');
				
			$search->addQuery($termQuery, BoolQuery::SHOULD);
			$search->addQuery($termQuery2, BoolQuery::SHOULD);
			$search->addAggregation($termsAggregationInstitution);
			$search->addAggregation($termsAggregationCollection);


			$results = $finder->findDocuments($search);

			$resultsArray=$this->parseElasticResult($results);
			
			return	 $this->render('NaturalheritageSearchBundle:Default:elasticsearch.html.twig', array('form'=>$form->createView(), 'results'=>$resultsArray["documents"], 'facets'=>$resultsArray["facets"]));
			//} catch(\Exception $e){
			   // print_r($e);
			 // }

		}
		else
		{
		
				return	 $this->render('NaturalheritageSearchBundle:Default:elasticsearch.html.twig', array('form'=>$form->createView()));
			
		}	
	}
	else
	{
		$errMsg=(string)$form->getErrors(true, false);
		$validityIssue=$form->getErrorsAsString();
		return $this->render('NaturalheritageSearchBundle:Default:error.html.twig', array("errorMsg"=>$errMsg, "validityIssue"=>$validityIssue));
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

	public function autocompleteAction($textpattern)
	{
		$hosts = [$this->getParameter('elastic_server_for_api')	];
		$clientBuilder = ClientBuilder::create();   // Instantiate a new ClientBuilder
		$clientBuilder->setHosts($hosts);           // Set the hosts
		$client = $clientBuilder->build();          // Build the client object
		$params = [
		    'index' => $this->getParameter('elastic_index'),
		    'type' => $this->getParameter('elastic_type'),
		    'body' => [
			'query' => [
			    'multi_match' => [
				'query' => $textpattern,
				'type' => 'phrase',
				'fields'=> ['content', 'content_ngrams']
			    ]
			],
			'highlight' => ['fields'    => array('content_ngrams' => new \stdClass(), 'content' => new \stdClass()),  'fragment_size' => 300]
		    ]
		];
		$patternregex = '/\b'.$textpattern.'[^\s]*?\b.*?(\.|$)/i';
		$results = $client->search($params);
		
		
		$returned=Array();
		foreach($results["hits"]["hits"] as $key=>$doc)
		{				
			$this->get_highlights($returned, $doc["highlight"], $patternregex, "content_ngrams");
			$this->get_highlights($returned, $doc["highlight"], $patternregex, "content");
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

	public function autocompleteselect2Action(Request $request)
	{
		 $key = $request->query->get('q');
		return $this->autocompleteAction($key); 
	}
}
