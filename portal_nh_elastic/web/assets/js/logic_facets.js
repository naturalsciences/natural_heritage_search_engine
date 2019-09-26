if(typeof jQuery ==="undefined")
{

	var script = document.createElement("script");
	script.src = "../vendor/jquery/dist/jquery.min.js";
	script.type = "text/javascript";
	document.getElementsByTagName('body')[0].appendChild(script);

	var script = document.createElement("script");
	script.src = "../vendor/select2/dist/js/select2.full.min.js";
	script.type = "text/javascript";
	document.getElementsByTagName('body')[0].appendChild(script);

}
var route;
var query_url;
var details_where_visible=false;
var details_what_visible=false;
var details_who_visible=false;
var details_where_init=false;
var details_what_init=false;
var details_who_init=false;


var detect_https=function(url)
{
	if (location.protocol == "https:") 
	{
		url=url.replace("http://","https://");
	}
	return url;
}


        
        
    var buildJsonParam=function(ctrl, concept, value)
	{
		var array_criteria=Array();
		var val = $(ctrl).val();
		if(val.length>0)
		{
			array_criteria=JSON.parse(val);
		}
		array_criteria.push({field:concept, term:value});
		$(ctrl).val(JSON.stringify(array_criteria));
	}

	var init_autocomplete=function()
	{

		route=$("#base_url").val();
		



		$('#elastic_search_institution').select2({
				//width: "300px",
				tags: true,
				tokenSeparators: ['|'],
				  ajax: {
				    url: detect_https(route.concat("autocompletegetall/institution")),
					processResults: function(data) {
				       return {results: data};
					}
				  }
				});
                
            var process_select2_data=function(id_ctrl)
             {
                var vals=Array();
                var tmp=$('#elastic_search_institution').select2('data');
                $.each($('#elastic_search_institution').select2('data'),
                        function(idx, tmpval)
                        {
                            vals.push(tmp[idx].id);
                        }
                    
                    );
                
                return vals.join("|");    
             }            
                
       		$('#elastic_search_collection').select2({
				//width: "300px",
				tags: true,
				tokenSeparators: ['|'],
				  ajax: {
				    url: detect_https(route.concat("autocompletegetall/collection")),
                    data: function (params) {
				      var query = {
					institutions: process_select2_data("#elastic_search_institution")
				      }	      
					
				      return query;
				    },
					processResults: function(data) {
				       return {results: data};
					}
				  }
				});



		$('#elastic_search_who').select2({
				//width: "300px",
				tags: true,
				tokenSeparators: ['|'],
				  ajax: {
				    url: detect_https(route.concat("autocompletewho")),
				    data: function (params) {
				      var query = {
					q: params.term
				      }	      
					
				      return query;
				    },
					processResults: function(data) {
					       return {results: data};
					}
				  }
				});
				$('#elastic_search_who').on(
					'select2:select',
					function(e)
					{
						var data = e.params.data;
						buildJsonParam("#facet_criteria_generic","who",data.id);
						
					}
				 );
                
        $('#elastic_search_where').select2({
				//width: "300px",
				tags: true,
				tokenSeparators: ['|'],
				  ajax: {
				    url: detect_https(route.concat("autocompletewhere")),
				    data: function (params) {
				      
				      var query = {
					q: params.term
				      }
				          
					
				      return query;
				    },
					processResults: function(data) {
					       return {results: data};
					}
				  }
				});
				$('#elastic_search_where').on(
					'select2:select',
					function(e)
					{
						var data = e.params.data;
						buildJsonParam("#facet_criteria_generic","where",data.id);
						
					}
				 );
                
        $('#elastic_search_what').select2({
				//width: "300px",
				tags: true,
				tokenSeparators: ['|'],
				  ajax: {
				    url: detect_https(route.concat("autocompletewhat")),
				    data: function (params) {
				      var query = {
					q: params.term
				      }

				      
					
				      return query;
				    },
					processResults: function(data) {
					       return {results: data};
					}
				  }
				});
                 $('#elastic_search_what').on(
					'select2:select',
					function(e)
					{
						var data = e.params.data;
						buildJsonParam("#facet_criteria_generic","what",data.id);
						
					}
				 );
                //$('.select2').on('select2:select', function () { $("select[id^=edit-term] option").each(function() { var val = $(this).val(); $(this).siblings("[value='"+ val +"']").remove(); }); });
               
                
      $('.date_picker_nh').datepicker({
            format: 'yyyy-mm-dd',
              });

	   		  
       $('.enable_details').click(
		function()
		{
            
			var iddiv=$(this).attr("id")+'_div';
			var keywordfield="";
			var flag_make_visible=true;
			var flag_init_ajax=false
			if($(this).attr("id")=="enable_details_who")
			{
				keywordfield="who";
				details_who_visible=!details_who_visible;
				
				if(!details_who_init)
				{
					details_who_init=true;
					flag_init_ajax=true;
				}
				else
				{
					if(details_who_visible)
					{
						$(".details_who").show();
					}
					else
					{
						$(".details_who").hide();
					}
				}

			}
			else if($(this).attr("id")=="enable_details_where")
			{
				keywordfield="where";
				 details_where_visible=!details_where_visible;
				 
				if(!details_where_init)
				{
					details_where_init=true;
					flag_init_ajax=true;
				}
				else
				{
					if(details_where_visible)
					{
						$(".details_where").show();
					}
					else
					{
						$(".details_where").hide();
					}
				}
			}
            else if($(this).attr("id")=="enable_details_what")
			{
			
				keywordfield="what";
				details_what_visible=!details_what_visible;
				
				if(!details_what_init)
				{	
					details_what_init=true;
					flag_init_ajax=true;
				}
				else
				{
					if(details_what_visible)
					{
						$(".details_what").show();
					}
					else
					{	
						$(".details_what").hide();
					}
				}
			}

			if(flag_init_ajax)
			{
				$.ajax(
						{
							type:"POST",
							url: detect_https(route.concat("detail_search_frame/"+keywordfield)),
							
							success: function(response)
							{
								$('#'+iddiv).html(response);
							}
						
									
						}
						);
			}
		}
        );

	}
$(document).ready(

    function()
    {
        init_autocomplete();
    }
);
