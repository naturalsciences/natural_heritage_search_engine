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
		$builder->add('submit', 'submit');
	}

	public function getName()
	{
		return 'elastic_search';
	}

	
}
