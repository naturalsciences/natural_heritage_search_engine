<?php

use Symfony\Component\HttpKernel\Kernel;
use Symfony\Component\Config\Loader\LoaderInterface;


class AppKernel extends Kernel
{
    public function registerBundles()
    {
        $bundles = array(
            new Symfony\Bundle\FrameworkBundle\FrameworkBundle(),
            new Symfony\Bundle\SecurityBundle\SecurityBundle(),
            new Symfony\Bundle\TwigBundle\TwigBundle(),
            new Symfony\Bundle\MonologBundle\MonologBundle(),
            new Symfony\Bundle\SwiftmailerBundle\SwiftmailerBundle(),
            new Doctrine\Bundle\DoctrineBundle\DoctrineBundle(),
            new Sensio\Bundle\FrameworkExtraBundle\SensioFrameworkExtraBundle(),
            new AppBundle\AppBundle(),
            new Naturalheritage\SearchBundle\NaturalheritageSearchBundle(),
	    #ftheeten 2017 10 24
	    //new FOS\ElasticaBundle\FOSElasticaBundle(),
	    //new Symfony\Component\Serializer\Serializer(),
	    //new JMS\SerializerBundle\JMSSerializerBundle(),
	    new ONGR\ElasticsearchBundle\ONGRElasticsearchBundle(),
	    new Braincrafted\Bundle\BootstrapBundle\BraincraftedBootstrapBundle(),
 	    new Tetranz\Select2EntityBundle\TetranzSelect2EntityBundle(),
	    new Symfony\Bundle\AsseticBundle\AsseticBundle(),
//new Elasticsearch\ClientBuilder();
        );

        if (in_array($this->getEnvironment(), array('dev', 'test'), true)) {
            $bundles[] = new Symfony\Bundle\DebugBundle\DebugBundle();
            $bundles[] = new Symfony\Bundle\WebProfilerBundle\WebProfilerBundle();
            $bundles[] = new Sensio\Bundle\DistributionBundle\SensioDistributionBundle();
            $bundles[] = new Sensio\Bundle\GeneratorBundle\SensioGeneratorBundle();
        }

        return $bundles;
    }

    public function registerContainerConfiguration(LoaderInterface $loader)
    {
        $loader->load($this->getRootDir().'/config/config_'.$this->getEnvironment().'.yml');
    }
}
