<?php

namespace Naturalheritage\SearchBundle\Form;

use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\Form\Extension\Core\Type\ChoiceType;
use Tetranz\Select2EntityBundle\Form\Type\Select2EntityType;

class ElasticSearchType extends AbstractType
{

	public function buildForm(FormBuilderInterface $builder, array $options)
	{
		//$builder->add('freetext', 'text');
 		//$builder->add('freetext', ChoiceType::class);
	/*$builder->add('freetext',  Select2EntityType::class, [
		    'multiple' => true,
		    'remote_route' => 'naturalheritage_search_autocompleteelasticsearch',
		    
		    'class' => 'Naturalheritage\SearchBundle\Entity\ElasticSearch',
		    'text_property' => 'textpattern',
		    'minimum_input_length' => 2,
		    'page_limit' => 10,
		    'placeholder' => 'type a word',
			'multiple'=> 'true'
		]);*/
		$builder->add('submit', 'submit');
	}

	public function getName()
	{
		return 'elastic_search';
	}

	
}
