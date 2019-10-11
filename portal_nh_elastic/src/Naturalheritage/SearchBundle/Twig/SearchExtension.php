<?php

// src/SearchBundle/Twig/SearchExtension.php
namespace Naturalheritage\SearchBundle\Twig;

use Twig\Extension\AbstractExtension;
use Twig\TwigFunction;

class SearchExtension extends AbstractExtension
{
     public function getFilters()
    {
        return array(
            new \Twig_SimpleFilter('md5', array($this, 'myMd5')),
        );
    }

    public function myMd5($str)
    {
        return md5($str);
    }
}