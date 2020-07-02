curl -X DELETE "localhost:9200/cetaf_passport?pretty"
#delete records


curl -X POST "localhost:9200/cetaf_passport/_delete_by_query?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match_all": {}
  }
}
'


#create

curl -X PUT "localhost:9200/cetaf_passport/_doc/BE-RBINS?routing=null&pretty" -H 'Content-Type: application/json' -d'
{
  "url_id":"http://collections.naturalsciences.be/cpb/nh-collections/countries/belgium/be-rbins",
  "main_type": "institution",
   "cetaf_institution":{
		"name":"Royal Belgian Institue for Natural Sciences",
		"description": "The Museum of Natural Sciences of Belgium (French: Muséum des sciences naturelles de Belgique, Dutch: Museum voor Natuurwetenschappen van België) is a museum dedicated to natural history, located in Brussels, Belgium.[2] The museum is a part of the Royal Belgian Institute of Natural Sciences. Its most important pieces are 30 fossilised Iguanodon skeletons, which were discovered in 1878 in Bernissart, Belgium. The dinosaur hall of the museum is the world'\''s largest museum hall completely dedicated to dinosaurs. Another famous piece is the Ishango bone, which was discovered in 1960 by Jean de Heinzelin de Braucourt in the Belgian Congo. The museum also houses a research department and a public exhibit department.",
		"identification_fields":
		{
		    "country_iso3166":"be",
			"country_en":"Belgium",
			"unique_acronym":"BE-RBINS",
			"grscicoll_code":"RBINS",
			"wikidata_id":"Q16665660",
			"grid_id":"grid.20478.39",
			"original_name":[
				{
					"iso639":"nl",
					"lang":"Dutch",
					"name":"Koninklijk Belgisch Instituut voor Natuurwetenschappen"
				},
				{
					"iso639":"fr",
					"lang":"French",
					"name":"Institut Royal des Sciences Naturelles de Belgique"
				}
			]
		}
   },
   "organisation":
   {
		"type_of_institution":["Museum","Research Institute"],
		"legal_status":"public",
		"if_part_of_a_larger_body": ["Belgian Sciences Policy (BELSPO)","Belgian General Directorate for Development Cooperation"],
		"address":
		{
			"street":"Rue Vautier / Vautierstraat 29",
			"city":"Brussels",
			"postcode":"1000",
			"country":"Belgium",
			"phone":"+32 (0)2 627 42 11",
			"email":"info@naturalsciences.be"
		}
   }
   ,
   "parent_relationship":
   {
		"name":"root",
		"parent":"null"
   }
}
'

#insert collection 1"
curl -X PUT "localhost:9200/cetaf_passport/_doc/BE-RBINS-ANT?routing=BE-RBINS&pretty" -H 'Content-Type: application/json' -d'
{
	"url_id":"http://collections.naturalsciences.be/cpb/nh-collections/collections-registry/anthropology-1",
	"main_type": "collection",
	"natural_history_collection":
	{
		"name":"Anthropology",
		"description":"Anthropology (main collection test)"
		
	   
	},
	"manager_head_of_collection":
		{
			"title":"Dr.",
			"name":"Patrick Semal",
			"position":"head of collections",
			"phone":"0032-2-627-43-80",
			"email":"patrick.semal@naturalsciences.be",
			"research_fields":"Anthropology"
		},
	"parent_relationship":
	   {
			"name":"root",
			"parent":"BE-RBINS"
	   }
}
'

#insert collection 2"
curl -X PUT "localhost:9200/cetaf_passport/_doc/BE-RBINS-ANT-ARC?routing=BE-RBINS-ANT&pretty" -H 'Content-Type: application/json' -d'
{
	"url_id":"http://collections.naturalsciences.be/cpb/nh-collections/countries/belgium/be-rbins/passport/2-cetaf-passport-collections/collections/anthropology/ant-arc",
	"main_type": "collection",
	"natural_history_collection":
	{
		"name":"Archeology",
		"description":"2Nd level collection"
		
	   
	},
	
	"manager_head_of_collection":
		{
			"title":"Dr.",
			"name":"Caroline Polet",
			
			
			"email":"caroline.polet@naturalsciences.be",
			"research_fields":["Anthropology","Paleontology"]
		},
	"parent_relationship":
	   {
			"name":"root",
			"parent":"BE-RBINS-ANT"
	   }
}
'