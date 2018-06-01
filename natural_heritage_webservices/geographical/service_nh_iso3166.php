<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$dbh = new PDO("pgsql:dbname=natural_heritage_gis_webservice;host=localhost", "postgres", "fv30714\$A"); 
$returned=Array();
if(array_key_exists("name",$_REQUEST))
{
    $levenshtein=1;
    if(array_key_exists("levenshtein",$_REQUEST))
    {
        $levenshtein=$_REQUEST['levenshtein'];
    }
    

    $value_to_test=$_REQUEST['name'];

   

    $query=$dbh->prepare("SELECT DISTINCT 
    iso3166_code ,
iso3166_name ,
iso3166_2_code,
iso3166_2_name ,
level2_subdivision_code ,
level2_subdivision_name,
levenshtein_distance

    FROM (SELECT *, unnest(regexp_split_to_array(unaccent(lower(search_field)), E'[^[:alnum:]]+'))
unnest_field,

unnest(regexp_split_to_array(unaccent(lower(?)), E'[^[:alnum:]]+')) unnest_searched,

levenshtein(search_field, ?) as levenshtein_distance FROM iso3166 
   
 ) a  

  WHERE 

    unnest_field=unnest_searched
    or levenshtein(unnest_field,unnest_searched)<=?
oRDER BY levenshtein_distance
    
    ;"
    
    );

    $query->execute(array($value_to_test,$value_to_test,$levenshtein));
    $returned= $query->fetchAll(PDO::FETCH_ASSOC);

}
if(array_key_exists("query",$_REQUEST))
{
    if($_REQUEST['query']=="iso3166_list")
    {           
            if(array_key_exists("namepattern",$_REQUEST))
            {
                        
                 $query=$dbh->prepare("SELECT DISTINCT 
                            iso3166_code ,
                            iso3166_name FROM iso3166
                            WHERE lower(iso3166_name) LIKE '%'||:namepattern::varchar||'%'
                            ORDER BY iso3166_name
                        ;"
                        
                        );

                        $query->execute(array($_REQUEST['namepattern']));
                        $returned= $query->fetchAll(PDO::FETCH_ASSOC);
                        
             }
             else
             {
                    $query=$dbh->prepare("SELECT DISTINCT 
                            iso3166_code ,
                            iso3166_name FROM iso3166
                            ORDER BY iso3166_name
                        ;"
                        
                        );

                        $query->execute();
                        $returned= $query->fetchAll(PDO::FETCH_ASSOC);
             }
    }    
    elseif($_REQUEST['query']=="subdivisions_list" &&array_key_exists("iso3166",$_REQUEST) )
    {           

            
            if(array_key_exists("namepattern",$_REQUEST))
            {
                $query=$dbh->prepare("SELECT DISTINCT *, 
                
                COALESCE(level2_subdivision_name,iso3166_2_name) as returned,
                COALESCE(level2_subdivision_code,iso3166_2_code) as returned_code
                    FROM
                    (SELECT 
                    iso3166_2_code ,
                    iso3166_2_name ,
                    level2_subdivision_code ,
                    CASE WHEN level2_subdivision_code IS NULL THEN NULL
                    ELSE
                        level2_subdivision_name 
                    END
                    FROM iso3166
                    WHERE LOWER(iso3166_code)=LOWER(:iso1)
                    AND iso3166_2_code IS NOT NULL
                    UNION
                    SELECT 
                    iso3166_2_code ,
                    iso3166_2_name ,
                    level2_subdivision_code ,
                    level2_subdivision_name 
                    FROM iso3166
                    WHERE LOWER(iso3166_code)=LOWER(:iso2)
                   
                    AND level2_subdivision_code IS NOT NULL) a 
                    WHERE LOWER(COALESCE(level2_subdivision_name,'')||COALESCE(iso3166_2_name,'')) LIKE '%'||:namepattern::varchar||'%'
                    ORDER BY iso3166_2_name                
                ;"
                
                );

                $query->execute(array($_REQUEST['iso3166'], $_REQUEST['iso3166'], strtolower($_REQUEST['namepattern'])));
                $returned= $query->fetchAll(PDO::FETCH_ASSOC);
            }
            else
            {
                $query=$dbh->prepare("SELECT DISTINCT *, COALESCE(level2_subdivision_name,iso3166_2_name) as returned,
                , COALESCE(level2_subdivision_code,iso3166_2_code) as returned_code
                    FROM
                    (SELECT 
                    iso3166_2_code ,
                    iso3166_2_name ,
                    level2_subdivision_code ,
                    CASE WHEN level2_subdivision_code IS NULL THEN NULL
                    ELSE
                        level2_subdivision_name 
                    END
                    FROM iso3166
                    WHERE LOWER(iso3166_code)=LOWER(:iso1)
                    AND iso3166_2_code IS NOT NULL
                    UNION
                    SELECT 
                    iso3166_2_code ,
                    iso3166_2_name ,
                    level2_subdivision_code ,
                    level2_subdivision_name 
                    FROM iso3166
                    WHERE LOWER(iso3166_code)=LOWER(:iso2)
                    AND level2_subdivision_code IS NOT NULL) a
                    ORDER BY iso3166_2_name                
                ;"
                
                );

                $query->execute(array($_REQUEST['iso3166'], $_REQUEST['iso3166']));
                $returned= $query->fetchAll(PDO::FETCH_ASSOC);
            }
    }
    elseif($_REQUEST['query']=="frompoint" &&array_key_exists("latitude",$_REQUEST)&&array_key_exists("latitude",$_REQUEST) &&array_key_exists("srs",$_REQUEST) )
    {
       
          $query=$dbh->prepare("SELECT 
          country as iso_3166_1_name, 
          iso_a2 as iso_3166_1, 
          iso_3166_2 , 
          name as iso_3166_2_name
          FROM public.v_ne_10m_admin_1_states_provinces_with_country
          WHERE st_contains(geom,ST_GEOMFROMTEXT('POINT(:longitude :latitude)', :srs))");
          $query->execute(array($_REQUEST['longitude'] , $_REQUEST['latitude'] ,$_REQUEST['srs'] ));          
         $returned= $query->fetchAll(PDO::FETCH_ASSOC);
          

    }
    
}
header('Content-Type: application/json');
print(json_encode($returned));
?>
