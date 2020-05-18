--exemple of call
--EX: SELECT * FROM georeferencing.call_nominatim_service('Meuse', 'BE', NULL, array['water', 'river']);
--4th parameter is the osm key/value for the type of feature
-- of SELECT *,  georeferencing.call_nominatim_service(name, 'iso3166', NULL, array['water', 'river']) FROM  gist_table;
--output
--
/*
TABLE(nominatim_result json, osm_result json, osm_id text, name_in_nominatim text, name_in_overpass text, osm_category text, osm_type text, longitude text, latitude text, geom geometry, geom_type text, wikidata_id text, date_query timestamp with time zone, url_nominatim character varying, url_osm_overpass character varying) 
*/
-->geom contains the polygon in PostGIS format


/*
FUNCTION 1 
AJAX WRAPPER

*/

--- Function: fct_rmca_py_webservice(text, text, text)

-- DROP FUNCTION fct_rmca_py_webservice(text, text, text);

--based on https://stackoverflow.com/questions/46540352/calling-restful-web-services-from-postgresql-procedure-function
CREATE OR REPLACE FUNCTION fct_rmca_py_webservice(uri text, body text DEFAULT NULL::text, content_type text DEFAULT 'application/json ; charset=utf-8'::text)
  RETURNS text AS
$BODY$
    import urllib
    import json
    from urllib import request,  error
    req = request.Request(uri)
    if body:
        req.add_data(body)
    if content_type:
        req.add_header('Content-Type', content_type)
    try:
        data = request.urlopen(req)
    except error.HTTPError as e:
        return None
    except error.URLError as e:
        if hasattr(e, 'reason'):
            return None
        elif hasattr(e, 'code'):
            return None
        else:
            return None
    else:
        ret = data.read().decode('utf-8')
        #plpy.notice(ret)
        if len(ret)==0:
            return None
        #plpy.notice(type(ret))
        tmp = json.loads(ret)
        if isinstance(tmp, int):
            return ret                   
        else:
            for k,v in tmp.items():
                #plpy.notice(v)
                #plpy.notice(type(v))
                if v:
                    if isinstance(v, str):
                        #plpy.notice("REPLACE")
                        tmp[k]=v.replace('"','\\"')
                        
        return json.dumps(tmp)
$BODY$
  LANGUAGE plpython3u VOLATILE
  COST 100;
ALTER FUNCTION fct_rmca_py_webservice(text, text, text)
  OWNER TO postgres;
GRANT EXECUTE ON FUNCTION fct_rmca_py_webservice(text, text, text) TO public;
GRANT EXECUTE ON FUNCTION fct_rmca_py_webservice(text, text, text) TO postgres;
GRANT EXECUTE ON FUNCTION fct_rmca_py_webservice(text, text, text) TO darwin2;

/*
FUNCTION 2 : map overpass data into PostGIS feature

*/

-- Function: georeferencing.call_overpass_id(character varying, character varying, character varying, text)

-- DROP FUNCTION georeferencing.call_overpass_id(character varying, character varying, character varying, text);

CREATE OR REPLACE FUNCTION georeferencing.call_overpass_id(IN p_osm_id character varying, IN p_name character varying, IN p_osm_type character varying DEFAULT 'relation'::character varying, IN p_url_osm text DEFAULT 'https://lz4.overpass-api.de/api/interpreter?data='::character varying)
  RETURNS TABLE(osm_id character varying, osm_response json, wikidata_id character varying, matched_name character varying, longitude character varying, latitude character varying, geom geometry, geom_type character varying, date_query timestamp with time zone, url character varying) AS
$BODY$

DECLARE
query_osm text;
tmp_osm jsonb;

r_id varchar;
r_json json;
r_wikidata_id varchar;
r_name varchar;
r_longitude varchar;
r_latitude varchar;
r_geom geometry;
r_geom_type varchar;
iterator jsonb;
 counter integer;
BEGIN 

r_id =NULL;
r_json  =NULL;
r_wikidata_id  =NULL;
r_name =NULL;
r_longitude =NULL;
r_latitude =NULL;
r_geom  =NULL;
r_geom_type =NULL;
query_osm=p_url_osm||urlencode('[out:json];'||p_osm_type||'('||p_osm_id||'); (._;>;);out;');
SELECT  fct_rmca_py_webservice(query_osm) into tmp_osm; 
--raise notice '%', tmp_osm;
IF tmp_osm is not null then
 r_id=p_osm_id;
 FOR iterator IN SELECT obj FROM jsonb_array_elements(tmp_osm->'elements') obj WHERE  obj->'tags' ? 'wikidata'  LOOP
	
	PERFORM  FROM jsonb_each_text(iterator->'tags') obj2 WHERE 
	key LIKE 'name:%' AND LOWER(value) ~ ('(^|\s)'||LOWER(p_name)||'($|\s)')::varchar ;   
	IF FOUND THEN
		r_wikidata_id=iterator->'tags'->>'wikidata';
		r_name=iterator->'tags'->>'name';
		r_json=iterator->'tags';
	END IF;
 END LOOP;

END IF;

RETURN QUERY 
SELECT 
r_id,
r_json ,
r_wikidata_id ,
r_name,
r_longitude ,
r_latitude ,
r_geom ,
r_geom_type ,
current_timestamp,
query_osm::varchar
;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION georeferencing.call_overpass_id(character varying, character varying, character varying, text)
  OWNER TO darwin2;


/*

Main function

*/
-- Function: georeferencing.call_nominatim_service(character varying, character varying, character varying, text[], text, text)

-- DROP FUNCTION georeferencing.call_nominatim_service(character varying, character varying, character varying, text[], text, text);

CREATE OR REPLACE FUNCTION georeferencing.call_nominatim_service(IN name character varying, IN iso_code character varying, IN p_osm_class character varying DEFAULT NULL::character varying, IN p_osm_types text[] DEFAULT NULL::text[], IN url text DEFAULT 'https://nominatim.openstreetmap.org/search?q='::character varying, IN url_osm text DEFAULT 'https://lz4.overpass-api.de/api/interpreter?data='::character varying)
  RETURNS TABLE(nominatim_result json, osm_result json, osm_id text, name_in_nominatim text, name_in_overpass text, osm_category text, osm_type text, longitude text, latitude text, geom geometry, geom_type text, wikidata_id text, date_query timestamp with time zone, url_nominatim character varying, url_osm_overpass character varying) AS
$BODY$
DECLARE

	srv_query varchar;
	length integer;
	tmp jsonb;
	elems jsonb;
	osm_id text;
	r_geom geometry;
	r_name text;
	r_categories text;
	r_type text;
	lat text;
	long text;
	r_type_geom text;
	r_osm_type text;
	query_osm text;
	tmp_osm jsonb;
	tags_osm jsonb;
	r_wikidata_id text;
	iterator jsonb;
	osm_matched_name varchar;
	rec record;
	curs REFCURSOR;
	
BEGIN


DROP  table if exists tmp_tbl ;
CREATE TEMPORARY TABLE IF NOT EXISTS 
tmp_tbl
(nominatim_result json, osm_result json, osm_id text, name_in_nominatim text, name_in_overpass text, osm_category text, osm_type text, longitude text, latitude text, geom geometry, geom_type text, wikidata_id text, date_query timestamp with time zone, url_nominatim varchar,
url_osm_overpass varchar)
ON COMMIT DROP;

tmp=NULL;
tmp_osm=NULL;
tags_osm=NULL;
r_geom=NULL;
 --osm_ids=NULL;
 r_name=NULL;
 r_categories=NULL;
 r_type=NULL;
lat=NULL;
long :=NULL;
r_type_geom:=NULL;
r_wikidata_id=NULL;
srv_query:=url||
					   
					   urlencode(name)					  
					  ||'&countrycodes='||urlencode(iso_code)
					  ||'&format=geojson&limit=100&polygon_geojson=1';
					  

RAISE NOTICE '%', srv_query;
--time out of 1.2 seconds
PERFORM pg_sleep('1.2');
SELECT  fct_rmca_py_webservice(srv_query) into tmp; 
RAISE NOTICE '%', tmp;
IF p_osm_class IS NULL AND p_osm_types IS NULL THEN
	OPEN curs FOR SELECT obj FROM jsonb_array_elements(tmp->'features') obj WHERE 
	(obj->'properties'->>'osm_type'='relation' OR obj->'properties'->>'osm_type'='way')
	;
ELSIF p_osm_class IS NOT NULL AND p_osm_types IS NULL THEN
--raise notice '2';
	OPEN curs FOR SELECT obj FROM jsonb_array_elements(tmp->'features') obj WHERE obj->'properties'->>'category'= p_osm_class
	AND (obj->'properties'->>'osm_type'='relation' OR obj->'properties'->>'osm_type'='way')
	;
ELSIF p_osm_class IS  NULL AND p_osm_types IS NOT NULL THEN
	--raise notice '3 % ', tmp;
	OPEN curs FOR SELECT obj FROM jsonb_array_elements(tmp->'features') obj  
	WHERE array_position( p_osm_types, obj->'properties'->>'type')>0   AND
	 (obj->'properties'->>'osm_type'='relation' OR obj->'properties'->>'osm_type'='way')
	 ;

	 
ELSIF p_osm_class IS  NOT NULL AND p_osm_types IS NOT NULL THEN
	OPEN curs FOR SELECT obj FROM jsonb_array_elements(tmp->'features') obj WHERE  obj->'properties'->>'category'= p_osm_class AND  array_position( p_osm_types, obj->'properties'->>'type')>0    AND (obj->'properties'->>'osm_type'='relation' OR obj->'properties'->>'osm_type'='way')
	 ;
END IF;

LOOP FETCH curs INTO iterator;
--raise notice '!!!!!!!';
 EXIT WHEN NOT FOUND;
SELECT osm_response, a.wikidata_id , matched_name, a.url INTO tags_osm, r_wikidata_id , osm_matched_name , query_osm FROM georeferencing.call_overpass_id(iterator->'properties'->>'osm_id', name) a;
		
		SELECT public.st_geomfromgeojson((iterator->'geometry')::text) INTO r_geom;
		r_type_geom=st_geometrytype(r_geom);
		If LOWER(r_type_geom)='st_linestring' THEN
			lat=st_y(ST_Line_Interpolate_Point(r_geom, 0.5));
			long=st_x(ST_Line_Interpolate_Point(r_geom, 0.5));
		ELSE
			lat=st_y(st_centroid(r_geom));
			long=st_x(st_centroid(r_geom));
		END IF;
		INSERT INTO tmp_tbl (nominatim_result,osm_id, name_in_nominatim, name_in_overpass, osm_category, osm_type,
wikidata_id,
 longitude,
 latitude,
 geom,
 geom_type
		, date_query, url_nominatim, url_osm_overpass
		 ) VALUES(tmp,iterator->'properties'->>'osm_id'
		,iterator->'properties'->>'display_name'
		, osm_matched_name
		,iterator->'properties'->>'category'
		,iterator->'properties'->>'osm_type',
		r_wikidata_id
		,
 long,
 lat,
 st_setsrid(r_geom,4326),
 r_type_geom,
		current_timestamp,
		srv_query,
		query_osm
		);
		
END LOOP;


RETURN query
SELECT * FROM tmp_tbl;


END ;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION georeferencing.call_nominatim_service(character varying, character varying, character varying, text[], text, text)
  OWNER TO postgres;
GRANT EXECUTE ON FUNCTION georeferencing.call_nominatim_service(character varying, character varying, character varying, text[], text, text) TO public;
GRANT EXECUTE ON FUNCTION georeferencing.call_nominatim_service(character varying, character varying, character varying, text[], text, text) TO postgres;
GRANT EXECUTE ON FUNCTION georeferencing.call_nominatim_service(character varying, character varying, character varying, text[], text, text) TO darwin2;
