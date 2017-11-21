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
			
			$(".nh_submit").click(
			
				function()
				{
					var base_url=route.concat("searchpartial/");
					query_url= base_url.concat($("#elastic_search_freetext").val());
					$.ajax(
					{
						type:"POST",
						url: query_url ,
						success: function(response)
						{
							$('#result_search').html(response);
						}
					
								
					}
					)
				});

			$('.select2').select2({
				//width: "300px",
				tags: true,
				multiple: false,
				  ajax: {
				    url: route.concat("autocompleteselect2"),
				    data: function (params) {
				      var query = {
					q: params.term
				      }

				      // Query parameters will be ?search=[term]&type=public
					
				      return query;
				    },
					processResults: function(data) {
					       return {results: data};
					}
				  }
				});



			PAGER={
			    pager_fct: function (page) {
					var base_url=query_url.concat("/").concat(page);
					$.ajax(
					{
						type:"POST",
						url: base_url,
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
