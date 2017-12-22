if(typeof jQuery ==="undefined")
{

	var script = document.createElement("script");
	script.src = "./assets/vendor/jquery/dist/jquery.min.js";
	script.type = "text/javascript";
	document.getElementsByTagName('body')[0].appendChild(script);

	var script = document.createElement("script");
	script.src = "./assets/vendor/select2/dist/js/select2.full.min.js";
	script.type = "text/javascript";
	document.getElementsByTagName('body')[0].appendChild(script);

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
				//var institutions=$("#elastic_search_institution").select2("val").join("|");
				//var authors=$("#elastic_search_authors").select2("val").join("|");
				if(!!$("#elastic_search_freetext").val())
				{				
					var criteria={};
                    criteria["fulltext"]=$("#elastic_search_freetext").val();
                    returned["fulltext"]=criteria;
				}
				if($("#elastic_search_institution").length)
				{				
					if($("#elastic_search_institution").select2("val").join("|").length>0)
					{	
                        var criteria={};    
						criteria["institutions"]=$("#elastic_search_institution").select2("val").join("|");
                        returned["institutions"]=criteria;
					}
				}
                
                if($("#elastic_search_collection").length)
				{				
					if($("#elastic_search_collection").select2("val").join("|").length>0)
					{	
                        var criteria={};    
						criteria["collections"]=$("#elastic_search_collection").select2("val").join("|");
                        returned["collections"]=criteria;
					}
				}
                
				if(("#elastic_search_who").length)
				{	
					if($("#elastic_search_who").select2("val").join("|").length>0)
					{	
                        var criteria={};                    
						criteria["who"]=$("#elastic_search_who").select2("val").join("|");
                        criteria["sub_category"]="*";
                        returned["who"]=criteria;
					
					}				
				}
                
                if(("#elastic_search_where").length)
				{	
					if($("#elastic_search_where").select2("val").join("|").length>0)
					{	
                        var criteria={};                    
						criteria["where"]=$("#elastic_search_where").select2("val").join("|");
                        criteria["sub_category"]="*";
                        returned["where"]=criteria;
					
					}				
				}
                
                if(("#elastic_search_what").length)
				{	
					if($("#elastic_search_what").select2("val").join("|").length>0)
					{	
                        var criteria={};                    
						criteria["what"]=$("#elastic_search_what").select2("val").join("|");
                        criteria["sub_category"]="*";
                        returned["what"]=criteria;
					
					}				
				}
                             
                if($("#elastic_search_when_start").val().length)
                {
                    if($("#elastic_search_when_start").val().length>0)
					{	
                        var criteria={};                    
						criteria["date_from"]=$("#elastic_search_when_start").val();
                        criteria["sub_category"]="*";
                        returned["date_from"]=criteria;
					}	
                }

                if($("#elastic_search_when_end").val().length)
                {
                    if($("#elastic_search_when_end").val().length>0)
					{	
            
						 var criteria={}; 
                         criteria["date_to"]=$("#elastic_search_when_end").val();
                         criteria["sub_category"]="*";
                         returned["date_to"]=criteria;
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
