<?php

namespace Naturalheritage\SearchBundle\Document;

use ONGR\ElasticsearchBundle\Annotation as ES;

/**
 * @ES\Document(type="document")
 */
class Document
{
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
    public $bundleName;

    /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $institution;


  
}

