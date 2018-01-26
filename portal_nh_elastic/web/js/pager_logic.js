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
				if($("#tmpN").length && $("#tmpS").length && $("#tmpW").length && $("#tmpE").length)
                {
                    if($("#tmpN").val().length && $("#tmpS").val().length && $("#tmpW").val().length && $("#tmpE").val().length)
                    {
                        if($("#tmpN").val().length>0 && $("#tmpS").val().length>0 && $("#tmpW").val().length>0 && $("#tmpE").val().length>0)
                        {
                            if($.isNumeric($("#tmpN").val()) && $.isNumeric($("#tmpS").val()) && $.isNumeric($("#tmpW").val()) && $.isNumeric($("#tmpE").val()))
                            {
                                var criteria={};
                                criteria["north"]=$("#tmpN").val();
                                criteria["west"]=$("#tmpW").val();
                                criteria["east"]=$("#tmpE").val();
                                criteria["south"]=$("#tmpS").val();
                                returned["bbox"]=criteria;

                            }
                        }
                    }
                }
				return returned;
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
			
		   
			var newValues=Array();
			var searchcopied=false;
			var history_select={};
			
			var add_to_history_select=function(key)
			{
					
					
					//alert(value);
				var id_history=key+"_history";
				var id_button=key+"_button";
				if(history_select.hasOwnProperty(key)==false)
				{
					history_select[key]=Array();
				}
				var values=Array();
				var value="";
				if($(key).hasClass("select2"))
				{
					value=$(key).select2("data");
					$.each(value, function(idx,obj){
						values.push(value[idx].text);
						});
				}
				else
				{
					value=$(key).val();
					values.push(value);					
				}
				$.each(values, function(idx, obj)
				{
					if(history_select[key].indexOf(values[idx])==-1)
					{	
						if(values[idx].length>0)
						{
							history_select[key].push(values[idx]);
							var $ctrl = $('<input/>').attr({ type: 'button', id:id_button, name:id_button,value:values[idx]}).addClass("likeananchor").addClass("history_click");
							$(id_history).append($ctrl);
							$(id_history).append("&nbsp;");
						}
					}	
				}
				
				);
									
				
				
			}
			KEEPSTATE={
				
				newValues:newValues,
				searchcopied:searchcopied,
				history_select:history_select,
				add_to_history_select:add_to_history_select
				
				
			}
			
			
			

	
			
		}
		

	);
	

	

