if(typeof jQuery ==="undefined")
{
alert('try');
	var script = document.createElement("script");
	script.src = "./assets/vendor/jquery/dist/jquery.min.js";
	script.type = "text/javascript";
	document.getElementsByTagName('body')[0].appendChild(script);

	var script = document.createElement("script");
	script.src = "./assets/vendor/select2/dist/js/select2.full.min.js";
	script.type = "text/javascript";
	document.getElementsByTagName('body')[0].appendChild(script);
alert('loaded');
}

var route;
var query_url;


$(document).ready(

		function()
		{	
			route=$("#base_url").val();
			
			function buildQuery()
			{
				returned={};
				var fulltext=$("#elastic_search_freetext").val();
				var institutions=$("#elastic_search_institution").select2("val").join("|");
				var authors=$("#elastic_search_authors").select2("val").join("|");
				if(!!$("#elastic_search_freetext").val())
				{				
					returned["fulltext"]=$("#elastic_search_freetext").val();
				}
				if($("#elastic_search_institution").length)
				{				
					if($("#elastic_search_institution").select2("val").join("|").length>0)
					{					
						returned["institutions"]=$("#elastic_search_institution").select2("val").join("|");
					}
				}
				if(("#elastic_search_authors").length)
				{	
					if($("#elastic_search_authors").select2("val").join("|").length>0)
					{				
						returned["authors"]=$("#elastic_search_authors").select2("val").join("|");
					
					}				
				}
				
				return returned;
			}

			var parseQueryArray=function(params)
			{
				
			}
			
			$(".nh_submit").click(
			
				function()
				{
				
					
					var base_url=route.concat("searchpartial");
					query_url= buildQuery();
					$.ajax(
					{
						type:"POST",
						url: base_url,
						data :query_url,
						success: function(response)
						{
							$('#result_search').html(response);
						}
					
								
					}
					)
				});			



			PAGER={
			    pager_fct: function (page) {
					query_url['page']=page;
					var base_url=$("#base_url").val();	
					base_url=base_url.concat("searchpartial");
					$.ajax(
					{
						type:"POST",
						url: base_url,
						data :query_url,
						success: function(response)
						{
							$('#result_search').html(response);
						}
					
								
					}
					)
			    }
			};

			
			
		}
	);
