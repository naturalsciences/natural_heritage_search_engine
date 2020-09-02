# natural_heritage_search_engine

This is the code source of the search portal of the Belspo Naturalheritage project. Writtent in Symfony2 / Symfony 3 (January 2019)
Two bundles have been developped :
-A front end for the ElasticSearch catalogue (PHP / JQuery / OpenLayers)
-an OAI-PMH web service implementing the Naoned interface
 (https://github.com/naoned/OaiPmhServerBundleà

## Example of OAI-PMH requests

 - https://darwin.naturalsciences.be/portal/app_dev.php/oaipmh/?verb=Identify

 - https://darwin.naturalsciences.be/portal/app_dev.php/oaipmh/?verb=ListSets

 - https://darwin.naturalsciences.be/portal/app_dev.php/oaipmh/?verb=ListIdentifiers&metadataPrefix=oai_dc

 - https://darwin.naturalsciences.be/portal/app_dev.php/oaipmh/?verb=ListRecords&metadataPrefix=oai_dc
