<?php

namespace Naturalheritage\SearchBundle\Document;

use ONGR\ElasticsearchBundle\Annotation as ES;

/**
 * @ES\Nested
 */
class Coordinates
{
     /**
     * @var string
     *
     * @ES\Property(type="text")
     */
    public $coordinates_point;
    
     /**
     * @var string
     *
     * @ES\Property(type="geo_point")
     */
    public $geo_ref_point;
}
