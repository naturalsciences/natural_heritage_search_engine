<?php

use Doctrine\Common\Annotations\AnnotationRegistry;
use Composer\Autoload\ClassLoader;

error_reporting(error_reporting() & ~E_USER_DEPRECATED);

/**
 * @var ClassLoader $loader
 */
$loader = require __DIR__.'/../vendor/autoload.php';

AnnotationRegistry::registerLoader(array($loader, 'loadClass'));

/*$loader->registerNamespaces(array(
    //[snip]
    'Elasticsearch'         => __DIR__.'/../vendor/elasticsearch/src', // the directory to contain the root namespace
));*/
$loader->add('Elasticsearch',__DIR__.'/../vendor/elasticsearch/src');



return $loader;
