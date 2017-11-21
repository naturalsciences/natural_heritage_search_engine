<?php

namespace Naturalheritage\SearchBundle\Entity;

use Symfony\Component\Serializer\Annotation\Groups;

/**
 * Document
 *
 */
class Document
{
    /**
     * @Groups({"elastica"})
     *
     * @var string
     */
    private $id;

    /**
     * @Groups({"elastica"})
     *
     * @var string
     */
    private $title;

    /**
     * @Groups({"elastica"})
     *
     * @var string
     */
    private $content;

    /**
     * @Groups({"elastica"})
     *
     * @var string
     */
    private $url;

    /**
     * @Groups({"elastica"})
     *
     * @var string
     */
    private $label;

    /**
     * @Groups({"elastica"})
     *
     * @var string
     */
    private $bundleName;

    /**
     * @Groups({"elastica"})
     *
     * @var string
     */
    private $institution;


    /**
     * Get id
     *
     * @return string
     */
    public function getId()
    {
        return $this->id;
    }

    /**
     * Set title
     *
     * @param string $title
     *
     * @return Document
     */
    public function setTitle($title)
    {
        $this->title = $title;

        return $this;
    }

    /**
     * Get title
     *
     * @return string
     */
    public function getTitle()
    {
        return $this->title;
    }

    /**
     * Set content
     *
     * @param string $content
     *
     * @return Document
     */
    public function setContent($content)
    {
        $this->content = $content;

        return $this;
    }

    /**
     * Get content
     *
     * @return string
     */
    public function getContent()
    {
        return $this->content;
    }

    /**
     * Set url
     *
     * @param string $url
     *
     * @return Document
     */
    public function setUrl($url)
    {
        $this->url = $url;

        return $this;
    }

    /**
     * Get url
     *
     * @return string
     */
    public function getUrl()
    {
        return $this->url;
    }

    /**
     * Set label
     *
     * @param string $label
     *
     * @return Document
     */
    public function setLabel($label)
    {
        $this->label = $label;

        return $this;
    }

    /**
     * Get label
     *
     * @return string
     */
    public function getLabel()
    {
        return $this->label;
    }

    /**
     * Set bundleName
     *
     * @param string $bundleName
     *
     * @return Document
     */
    public function setBundleName($bundleName)
    {
        $this->bundleName = $bundleName;

        return $this;
    }

    /**
     * Get bundleName
     *
     * @return string
     */
    public function getBundleName()
    {
        return $this->bundleName;
    }

    /**
     * Set institution
     *
     * @param string $institution
     *
     * @return Document
     */
    public function setInstitution($institution)
    {
        $this->institution = $institution;

        return $this;
    }

    /**
     * Get institution
     *
     * @return string
     */
    public function getInstitution()
    {
        return $this->institution;
    }
}

