<?php

namespace Naturalheritage\OaipmhBundle\OaiPmh;

use Naoned\OaiPmhServerBundle\OaiPmh\OaiPmhRuler as BaseRuler;


class OaiPmhRulerNh extends BaseRuler
{
	const CACHE_PREFIX = 'oaipmh_';
    const DEFAULT_STARTS = 0;

    private $countPerLoad;
	protected $total;
	protected $elastic_resumption;
	
	private static function getcacheKey($token)
    {
        return self::CACHE_PREFIX.$token;
    }

	
    private static $availableMetadata = array(
        // This server currently supports only oai_dc Data format
        'oai_dc' => array(
           'schema'            => 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
           'metadataNamespace' => 'http://www.openarchives.org/OAI/2.0/oai_dc/',
        )
    );
	
	public function setTotal($value)
	{
		$this->total=$value;
	}
	
	public function setCountPerLoad($countPerLoad)
    {
        $this->countPerLoad = $countPerLoad;
    }
	
    public function setElasticResumption($value)
    {
        $this->elastic_resumption = $value;
    }
    
     public function getSearchParams($queryParams, $cache)
    {
        $searchParams=parent::getSearchParams($queryParams, $cache);
        if (array_key_exists('resumptionToken', $queryParams)  ) 
        {
            //$searchParams['previous_token'] = $queryParams["resumptionToken"];
        }
        else
        {
            $searchParams['record_starts'] = self::DEFAULT_STARTS;
            $searchParams['previous_token'] = "";
        }
        
        return $searchParams;
    }
    
    public function getResumption($items, $searchParams, $cache)
    {

         $resumption = array();
         $resumption['next'] = false;
         $nbPages=floor($this->total / $this->countPerLoad)+1;
         $currentStartRecord=$searchParams['record_starts'];
         $currentPage=floor($currentStartRecord / $this->countPerLoad)+1;
         if($currentPage<$nbPages  )
         {   
 
            $currentStartRecord = $currentStartRecord + count($items);
            $resumption['next']       = true;
            $resumption['token']      = $this->elastic_resumption;
            $resumption['expiresOn']  = time() + 604800;
            $resumption['totalCount'] = $this->total;
            $cache->save(
                $this->getcacheKey($resumption['token']),
                array_merge(
                    $searchParams,
                    array(                        
                        'starts' => 0,
                        'record_starts' => $currentStartRecord  ,
                        'ends'   =>  $this->countPerLoad -1,
                        'nb_pages' => $nbPages,
                        'current_page' =>  $currentPage,
                        'previous_token' =>  $resumption['token'],
                    )
                )
            );
         }

        $resumption['starts'] = 0; 
        $resumption['record_starts'] = $currentStartRecord;         
        $resumption['ends'] = min($this->countPerLoad -1, count($items)-1);
        $resumption['totalCount'] = $this->total;
        $resumption['items'] = $items;
        $resumption['isFirst'] = $resumption['starts'] == self::DEFAULT_STARTS;
        $resumption['isLast'] = $currentPage == $nbPages;
        $resumption['current_page'] = $currentPage;
        $resumption['page_size'] = $this->countPerLoad;
        return $resumption;
    }
	

}
