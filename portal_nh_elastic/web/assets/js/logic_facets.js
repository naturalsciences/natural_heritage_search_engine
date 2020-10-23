if (typeof jQuery === "undefined") {

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
var details_where_visible = false;
var details_what_visible = false;
var details_who_visible = false;
var details_where_init = false;
var details_what_init = false;
var details_who_init = false;

var elastic_search_what_and = "or";
var elastic_search_where_and = "or";
var elastic_search_who_and = "or";

var globalListCtrls = new Object();
var globalListBoolean = new Object();

var globalListCtrlsGeneric = new Object();
var globalListBooleanGeneric = new Object();

var globalListCtrlsAnnex = new Object();
var globalListBooleanAnnex = new Object();

var GLOBAL_WFS_GEOM='';
var GLOBAL_WFS_ARRAY=Array();
var GLOBAL_LAYER_ARRAY=Array();


var detect_https = function(url) {
    if (location.protocol == "https:") {
        url = url.replace("http://", "https://");
    }
    return url;
}


var toggleDetails = function() {
    if (show_details) {
        $(".detailed_search").show();
        $("#toggle_details").attr("value", "Hide details");
    } else {

        $(".detailed_search").hide();
        $("#toggle_details").attr("value", "View details");
    }
}

var test_map_visibility = function(is_visible) {
    if (is_visible) {

        $("#main_map_container_nh").show();
        MAP.map.updateSize();
        $("#show_map").prop("value", "Hide map");
    } else {
        $("#main_map_container_nh").hide();
        $("#show_map").prop("value", "Show map");
		$(".wkt_search").val('');
		$("#tmpN").val('');
		$("#tmpW").val('');
		$("#tmpS").val('');
		$("#tmpE").val('');
		GLOBAL_WFS_GEOM='';
        GLOBAL_WFS_ARRAY=Array();
		GLOBAL_LAYER_ARRAY=Array();
		$("#wkt_search").val('');
		$("#wfs_search").val('');
		$("#chosen_layer").val('');
    }
}




var buildJsonParamArray = function(ctrl, concept, values, operator) {
    var array_criteria = Array();
    var val = $(ctrl).val();
    if (val.length > 0) {
        array_criteria = JSON.parse(val);

        array_criteria = array_criteria.filter(
            function(e) {
                return e.term !== concept;
            }
        );
    }
    for (var i = 0; i < values.length; i++) {
        array_criteria.push({
            field: concept,
            term: values[i],
            operator: operator
        });
    }
    //console.log(array_criteria);
    $(ctrl).val(JSON.stringify(array_criteria));
}

var buildJsonParam = function(ctrl, concept, value) {
    var array_criteria = Array();
    var val = $(ctrl).val();
    if (val.length > 0) {
        array_criteria = JSON.parse(val);
    }
    array_criteria.push({
        field: concept,
        term: value
    });
    $(ctrl).val(JSON.stringify(array_criteria));
}

//important main search criteria builder
var rebuildSearch = function() {
    $("#facet_criteria").val("");
    $("#facet_criteria_generic").val("");
    $("#facet_criteria_annex").val("");

    $.each(globalListCtrls, function(key, value) {
        buildJsonParamArray("#facet_criteria", key, $(value).val(), globalListBoolean[key]);
    });
    $.each(globalListCtrlsGeneric, function(key, value) {
        buildJsonParamArray("#facet_criteria_generic", key, $(value).val(), globalListBooleanGeneric[key]);
    });

    $.each(globalListCtrlsAnnex, function(key, value) {
        if (key == "institution") {
            buildJsonParamArray("#facet_criteria_annex", key, $(value).val(), globalListBooleanAnnex[key]);
        } else if (key == "collection") {
            buildJsonParamArray("#facet_criteria_annex", "all_collections", $(value).val(), globalListBooleanAnnex[key]);
            //buildJsonParamArray( "#facet_criteria_annex", "sub_collection", $(value).val(), globalListBooleanAnnex[key] );
        }
    });

}

var select_generic = function(target, ctrl, val_and_or, criteria) {

    var operator = "or";

    if (val_and_or == "and") {
        operator = "and";
    }

    var tmpArray = ctrl.val();
    if (tmpArray.length > 0) {

        buildJsonParamArray(target, criteria, tmpArray, operator);

    }
}

var init_autocomplete = function() {

    route = $("#base_url").val();




    $('#elastic_search_institution').select2({
        //width: "300px",
        tags: true,
        tokenSeparators: ['|'],
        ajax: {
            url: detect_https(route.concat("autocompletegetall/institution")),
            processResults: function(data) {
                return {
                    results: data
                };
            }
        }
    });

    var process_select2_data = function(id_ctrl) {
        var vals = Array();
        var tmp = $('#elastic_search_institution').select2('data');
        $.each($('#elastic_search_institution').select2('data'),
            function(idx, tmpval) {
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
            data: function(params) {
                var query = {
                    institutions: process_select2_data("#elastic_search_institution")
                }

                return query;
            },
            processResults: function(data) {
                return {
                    results: data
                };
            }
        }
    });



    $('#elastic_search_who').select2({
        //width: "300px",
        tags: true,
        tokenSeparators: ['|'],
        ajax: {
            url: detect_https(route.concat("autocompletewho")),
            data: function(params) {
                var query = {
                    q: params.term
                }

                return query;
            },
            processResults: function(data) {
                return {
                    results: data
                };
            }
        }
    });

    $('#elastic_search_who').on(
        'select2:select',
        function(e) {
            select_generic(
                "#facet_criteria_generic",
                $(this),
                elastic_search_who_and,
                'who');
        }
    );

    $('#elastic_search_where').select2({
        //width: "300px",
        tags: true,
        tokenSeparators: ['|'],
        ajax: {
            url: detect_https(route.concat("autocompletewhere")),
            data: function(params) {

                var query = {
                    q: params.term
                }


                return query;
            },
            processResults: function(data) {
                return {
                    results: data
                };
            }
        }
    });
    $('#elastic_search_where').on(
        'select2:select',
        function(e) {
            select_generic(
                "#facet_criteria_generic",
                $(this),
                elastic_search_where_and,
                'where');
        }
    );

    $('#elastic_search_what').select2({
        //width: "300px",
        tags: true,
        tokenSeparators: ['|'],
        ajax: {
            url: detect_https(route.concat("autocompletewhat")),
            data: function(params) {
                var query = {
                    q: params.term
                }



                return query;
            },
            processResults: function(data) {
                return {
                    results: data
                };
            }
        }
    });
    $('#elastic_search_what').on(
        'select2:select',
        function(e) {
            select_generic(
                "#facet_criteria_generic",
                $(this),
                elastic_search_what_and,
                'what');
        }
    );

    $("#elastic_search_where_and").click(
        function() {
            if ($("#elastic_search_where_and").is(':checked')) {
                globalListBooleanGeneric["where"] = "and";
            } else {
                globalListBooleanGeneric["where"] = "or";
            }


        }
    );

    $("#elastic_search_what_and").click(
        function() {
            if ($("#elastic_search_what_and").is(':checked')) {
                globalListBooleanGeneric["what"] = "and";
            } else {
                globalListBooleanGeneric["what"] = "or";
            }


        }
    );

    $("#elastic_search_who_and").click(
        function() {
            if ($("#elastic_search_who_and").is(':checked')) {
                globalListBooleanGeneric["who"] = "and";
            } else {
                globalListBooleanGeneric["who"] = "or";
            }


        }
    );

    $("#elastic_search_institution_and").click(
        function() {
            if ($("#elastic_search_institution_and").is(':checked')) {
                globalListBooleanAnnex["institution"] = "and";
            } else {
                globalListBooleanAnnex["institution"] = "or";
            }


        }
    );

    $("#elastic_search_collection_and").click(
        function() {
            if ($("#elastic_search_collection_and").is(':checked')) {
                globalListBooleanAnnex["collection"] = "and";
            } else {
                globalListBooleanAnnex["collection"] = "or";
            }


        }
    );
    //$('.select2').on('select2:select', function () { $("select[id^=edit-term] option").each(function() { var val = $(this).val(); $(this).siblings("[value='"+ val +"']").remove(); }); });

    $('#when_start_type').select2({
        //width: "300px",
        tags: true,
        tokenSeparators: ['|'],
        ajax: {
            url: detect_https(route.concat("date_types")),
            data: function(params) {
                var query = {
                    q: params.term
                }



                return query;
            },
            processResults: function(data) {
                return {
                    results: data
                };
            }
        }
    });
    $('#when_end_type').select2({
        //width: "300px",
        tags: true,
        tokenSeparators: ['|'],
        ajax: {
            url: detect_https(route.concat("date_types")),
            data: function(params) {
                var query = {
                    q: params.term
                }



                return query;
            },
            processResults: function(data) {
                return {
                    results: data
                };
            }
        }
    });
    $('.date_picker_nh').datepicker({
        format: 'yyyy-mm-dd',
    });


    //enable_details
    $('.enable_details').click(
        function() {

            var iddiv = $(this).attr("id") + '_div';
            var keywordfield = "";
            var flag_make_visible = true;
            var flag_init_ajax = false
            if ($(this).attr("id") == "enable_details_who") {
                keywordfield = "who";
                details_who_visible = !details_who_visible;

                if (!details_who_init) {
                    details_who_init = true;
                    flag_init_ajax = true;
                } else {
                    if (details_who_visible) {
                        $(".details_who").show();
                    } else {
                        $(".details_who").hide();
                    }
                }

            } else if ($(this).attr("id") == "enable_details_where") {
                keywordfield = "where";
                details_where_visible = !details_where_visible;

                if (!details_where_init) {
                    details_where_init = true;
                    flag_init_ajax = true;
                } else {
                    if (details_where_visible) {
                        $(".details_where").show();
                    } else {
                        $(".details_where").hide();
                    }
                }
            } else if ($(this).attr("id") == "enable_details_what") {

                keywordfield = "what";
                details_what_visible = !details_what_visible;

                if (!details_what_init) {
                    details_what_init = true;
                    flag_init_ajax = true;
                } else {
                    if (details_what_visible) {
                        $(".details_what").show();
                    } else {
                        $(".details_what").hide();
                    }
                }
            }

            if (flag_init_ajax) {
                $.ajax({
                    type: "POST",
                    url: detect_https(route.concat("detail_search_frame/" + keywordfield)),

                    success: function(response) {
                        $('#' + iddiv).html(response);
                    }


                });
            }
        }
    );

}
//2020 09 01
var getStorageData=function()
{
   
    var returned="";
    if (sessionStorage.getItem("es_result") !== null) {
        //console.log("TEST_2");
        returned=sessionStorage.getItem("es_result");
    }
    return returned;
}
//2020 09 01 
var reinitPostParamWithStorageData=function(data)
{	
	
    if (sessionStorage.getItem("es_result") !== null) {
        //console.log("TEST_2");
        data["es_result"]=sessionStorage.getItem("es_result");
    }
	
	data["expanded"] = false;
    if ($("#facet_criteria").val().length > 0) {
        data["extra_params"] = JSON.stringify($("#facet_criteria").val());
        data["expanded"] = true;
    }
	if ($("#facet_criteria_facets").val().length > 0) {
        data["extra_params_facets"] = JSON.stringify($("#facet_criteria_facets").val());
        data["expanded"] = true;
    }
	
	if ($("#facet_criteria_annex").val().length > 0) {
        data["extra_params_annex"] = JSON.stringify($("#facet_criteria_annex").val());
        data["expanded"] = true;
    }

    if ($("#facet_criteria_annex_facets").val().length > 0) {
		
        data["extra_params_annex_facets"] = JSON.stringify($("#facet_criteria_annex_facets").val());
        data["expanded"] = true;
    }
 
    return data;
}

//main search function	
var search_fct = function(page, load_facets) {
    var url = route.concat("es_wrapper");
    var result_url = route.concat("result_facets");
    var facet_url = route.concat("detail_facets");

    //reset
	//2020 09 01
	if(load_facets)
	{
		rebuildSearch();
	}
    var criterias = {};
    criterias["page"] = page;
    if ($("#elastic_search_freetext").val()) {
        if ($("#elastic_search_freetext").val().length > 0) {
            var term = $("#elastic_search_freetext").val();
            if (term.length > 0) {
                criterias["term"] = term;
            }
        }
    }
	
	if ($("#elastic_search_cetaf_collections").val()) {
        if ($("#elastic_search_cetaf_collections").val().length > 0) {
            var cetaf_collection = $("#elastic_search_cetaf_collections").val();
            if (cetaf_collection.length > 0) {
                criterias["cetaf_collection"] = cetaf_collection;
            }
        }
    }
	
    criterias["expanded"] = false;
    if ($("#facet_criteria").val().length > 0) {

        criterias["extra_params"] = $("#facet_criteria").val();
        criterias["expanded"] = true;
    }
    if ($("#facet_criteria_generic").val().length > 0) {

        criterias["extra_params_generic"] = $("#facet_criteria_generic").val();
        criterias["expanded"] = true;
    }
    if ($("#facet_criteria_annex").val().length > 0) {
        criterias["extra_params_annex"] = $("#facet_criteria_annex").val();
        criterias["expanded"] = true;
    }
    if ($("#facet_criteria_facets").val().length > 0) {

        criterias["extra_params_facets"] = $("#facet_criteria_facets").val();
        criterias["expanded"] = true;
    }

    if ($("#facet_criteria_annex_facets").val().length > 0) {
        criterias["extra_params_annex_facets"] = $("#facet_criteria_annex_facets").val();
        criterias["expanded"] = true;
    }
    if ($("#tmpN").val().length > 0 && $("#tmpW").val().length > 0 && $("#tmpE").val().length > 0 && $("#tmpS").val().length > 0) {
        criterias["coordinates"] = $("#tmpW").val() + ";" + $("#tmpE").val() + ";" + $("#tmpS").val() + ";" + $("#tmpN").val();
    }

    if ($("#elastic_search_when_start").val().length) {
        if ($("#elastic_search_when_start").val().length > 0) {
            criterias["date_from_type"] = $("#when_start_type").val().join("|");
            criterias["date_from"] = $("#elastic_search_when_start").val();

        }
    }

    if ($("#elastic_search_when_end").val().length) {
        if ($("#elastic_search_when_end").val().length > 0) {
            criterias["date_to_type"] = $("#when_end_type").val().join("|");
            criterias["date_to"] = $("#elastic_search_when_end").val();

        }
    }
	
	if ($("#wkt_search").val().length) {
        if ($("#wkt_search").val().length > 0) {
            criterias["wkt_search"] = $("#wkt_search").val();
        }
    }
	if(GLOBAL_WFS_GEOM.length>0)
	{
		criterias["wfs_search"] = GLOBAL_WFS_GEOM;
	}

	criterias["es_result"] = getStorageData();
    var dataTmp = criterias;

    var dataTmp2 = {};

    dataTmp2["page"] = page;
	
	dataTmp2["es_result"] = getStorageData();
	dataTmp2["expanded"] = false;
    if ($("#facet_criteria").val().length > 0) {

        dataTmp2["extra_params"] = $("#facet_criteria").val();
        dataTmp2["expanded"] = true;
    }
	if ($("#facet_criteria_facets").val().length > 0) {

        dataTmp2["extra_params_facets"] = $("#facet_criteria_facets").val();
        dataTmp2["expanded"] = true;
    }
	
	if ($("#facet_criteria_annex").val().length > 0) {

        dataTmp2["extra_params_annex"] = $("#facet_criteria_annex").val();
        dataTmp2["expanded"] = true;
    }

    if ($("#facet_criteria_annex_facets").val().length > 0) {
        dataTmp2["extra_params_annex_facets"] = $("#facet_criteria_annex_facets").val();
        dataTmp2["expanded"] = true;
    }

    if (Object.keys(dataTmp).length > 0) {
        $.ajax({
                url: detect_https(url),
				 method: "POST",
                data: dataTmp,
                dataType: "json",
                success: function(data) {
                    //console.log(data);
					//2020 09 01
                    sessionStorage.setItem("es_result", JSON.stringify(data));
                    //tmpData=JSON.parse(sessionStorage.getItem("es_result"));
                    //console.log(tmpData);
                    $.ajax({
                        url: detect_https(result_url),
						
                        data: reinitPostParamWithStorageData(dataTmp2),
                        dataType: "html",
						 method: "POST",
                        success: function(data) {
                            //sessionStorage.setItem("result_facets", JSON.stringify(data));
							
                            $("#searchCont").html(data);
							/*
                            $("#facet_criteria").val("");
                            $("#facet_criteria_generic").val("");
                            $("#facet_criteria_annex").val("");
                            $("#facet_criteria_facets").val("");
                            $("#facet_criteria_annex_facets").val("");
							*/
                            $(".nh_spinner").hide();
                        },
                    });
                    if (load_facets) {
                        $.ajax({
                            url: detect_https(facet_url),
                            data: reinitPostParamWithStorageData(dataTmp2),
                            dataType: "html",
							method: "POST",
                            success: function(data) {
                                sessionStorage.setItem("detail_facets", JSON.stringify(data));
                                $("#placeholder_facets").html(data);
                                $(".nh_spinner").hide();
                            },
                        });
                    }
                },

            }

        );

    }
}



$(document).ready(

    function() {
        init_autocomplete();

        //register
        globalListCtrlsGeneric["what"] = "#elastic_search_what";
        globalListBooleanGeneric["what"] = 'or';
        globalListCtrlsGeneric["who"] = "#elastic_search_who";
        globalListBooleanGeneric["who"] = '#or';
        globalListCtrlsGeneric["where"] = "#elastic_search_where";
        globalListBooleanGeneric["where"] = 'or';

        globalListCtrlsAnnex["institution"] = "#elastic_search_institution";
        globalListBooleanAnnex["institution"] = 'or';
        globalListCtrlsAnnex["collection"] = "#elastic_search_collection";
        globalListBooleanAnnex["collection"] = 'or';




        var back_url = route.concat("back");
        if (window.history && window.history.pushState) {

            history.pushState("nohb", null, "");

            $(window).on("popstate", function(event) {
                if (!event.originalEvent.state) {
                    $.ajax({
                        url: detect_https(back_url),
                        dataType: "html",
                        success: function(data) {
                            //console.log(data);
                            $("#elastic_search_freetext").val("");
                            $("#facet_criteria").val("");
                            $("#facet_criteria_generic").val("");
                            $("#facet_criteria_annex").val("");
                            $("#facet_criteria_facets").val("");
                            $("#facet_criteria_annex_facets").val("");
                            var data_obj = JSON.parse(data);
                            if ("term" in data_obj) {
                                //console.log(data_obj["term"]);
                                var option = new Option(data_obj["term"], data_obj["term"], true, true);
                                $("#elastic_search_freetext").append(option).trigger('change');

                            }

                        },
                    });
                    return;
                }
            });
        }

        $(".toggle_details").click(
            function() {
                show_details = !show_details;
                toggleDetails();
            }
        );

        $(".show_map").click(
            function() {
                map_visible = !map_visible;
                test_map_visibility(map_visible);
            }
        );

        $(".simple_search").click(
            function() {
                map_visible = false;
                show_details = false;
                toggleDetails();
                test_map_visibility(map_visible);
                $("#facet_criteria").val("");
                $("#facet_criteria_generic").val("");
                $("#facet_criteria_annex").val("");
                $("#facet_criteria_facets").val("");
                $("#facet_criteria_annex_facets").val("");
                $(".memoryforfacet").not("#elastic_search_freetext").val(null).trigger('change');
            }
        );
        
        

        

        $(document).keypress(function(e) 
        { 
            if (e.which === 13) {
                 e.preventDefault();               
                 $("#search_dem").click();
            }
        });


       $(".clear_all").click(function()
           {                
                $("#facet_criteria").val("");
                $("#facet_criteria_generic").val("");
                $("#facet_criteria_annex").val("");
                $("#facet_criteria_facets").val("");
                $("#facet_criteria_annex_facets").val("");
                $("#elastic_search_freetext").val(null).trigger('change');
                $(".select2").val(null).trigger('change');
                $("input:checkbox").prop('checked', $(this).prop("checked"));
                $(".date_picker_nh").val("");
            
           }
       );

    }
);