<?php

namespace Naturalheritage\SearchBundle\Document;

use ONGR\ElasticsearchBundle\Annotation as ES;
use Doctrine\Common\Collections\ArrayCollection;
/**
 * @ES\Document(type="document")
 */
class Document
{

    public function __construct()
    {
        $this->object_identifiers = new ArrayCollection();
    }
    
    /**
     * @var string
     *
     * @ES\Id()
     */
    public $id;

   /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $title;

   /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $content;

    /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $url;

   /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $label;

    /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $main_collection;
    
   /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $sub_collection;
    
     /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $object_type;

    /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $institution;
    
    
    /**
     * @var ContentMetaObject
     *
     * @ES\Embedded(class="NaturalheritageSearchBundle:ObjectIdentifiers", multiple=true)
     */
    public $object_identifiers;
    
    
  
}

