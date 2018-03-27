<?php

namespace Naturalheritage\SearchBundle\Document;

use ONGR\ElasticsearchBundle\Annotation as ES;

/**
 * @ES\Nested
 */
class ObjectIdentifiers
{
     /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $identifier;
    
     /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $identifier_type;
}