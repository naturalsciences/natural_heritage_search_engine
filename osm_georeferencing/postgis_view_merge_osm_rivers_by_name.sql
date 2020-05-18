-- View: wfs.v_belgian_rivers_osm_20200402_name_cluster

-- DROP VIEW wfs.v_belgian_rivers_osm_20200402_name_cluster;


/*
-- Table: wfs.belgian_rivers_osm_20200402

-- DROP TABLE wfs.belgian_rivers_osm_20200402;

CREATE TABLE wfs.belgian_rivers_osm_20200402
(
  gid integer NOT NULL DEFAULT nextval('wfs."wfs.belgian_rivers_osm_20200402_gid_seq"'::regclass),
  geom geometry(LineString,4326),
  id character varying,
  "@id" character varying,
  boat character varying,
  name character varying,
  "natural" character varying,
  waterway character varying,
  "CEMT" character varying,
  "name:ru" character varying,
  "name:fr" character varying,
  "name:nl" character varying,
  tidal character varying,
  intermittent character varying,
  layer character varying,
  created_by character varying,
  tunnel character varying,
  wikidata character varying,
  alt_name character varying,
  "name:language" character varying,
  history character varying,
  description character varying,
  "ref:VHAG" character varying,
  wikipedia character varying,
  width character varying,
  note character varying,
  source character varying,
  "name:wa" character varying,
  "name:lb" character varying,
  "name:lt" character varying,
  admin_level character varying,
  boundary character varying,
  "name:de" character varying,
  "name:en" character varying,
  "name:he" character varying,
  "name:hu" character varying,
  motorboat character varying,
  "wikipedia:de" character varying,
  "wikipedia:en" character varying,
  "wikipedia:nl" character varying,
  "name:be" character varying,
  "name:et" character varying,
  "name:hy" character varying,
  "name:zh" character varying,
  fixme character varying,
  canoe character varying,
  "name:af" character varying,
  "name:ar" character varying,
  "name:bg" character varying,
  "name:bn" character varying,
  "name:br" character varying,
  "name:ca" character varying,
  "name:cs" character varying,
  "name:cy" character varying,
  "name:da" character varying,
  "name:el" character varying,
  "name:eo" character varying,
  "name:es" character varying,
  "name:eu" character varying,
  "name:fa" character varying,
  "name:fi" character varying,
  "name:fy" character varying,
  "name:gl" character varying,
  "name:hr" character varying,
  "name:it" character varying,
  "name:ja" character varying,
  "name:ka" character varying,
  "name:ko" character varying,
  "name:la" character varying,
  "name:li" character varying,
  "name:lv" character varying,
  "name:mk" character varying,
  "name:nn" character varying,
  "name:no" character varying,
  "name:oc" character varying,
  "name:pl" character varying,
  "name:pt" character varying,
  "name:ro" character varying,
  "name:sh" character varying,
  "name:si" character varying,
  "name:sk" character varying,
  "name:sr" character varying,
  "name:sv" character varying,
  "name:ta" character varying,
  "name:th" character varying,
  "name:tl" character varying,
  "name:tr" character varying,
  "name:uk" character varying,
  "name:vi" character varying,
  lock character varying,
  "seamark:type" character varying,
  maxheight character varying,
  short_name character varying,
  ref character varying,
  "lock:name" character varying,
  "lock:VHF_channel" character varying,
  "lock:phone" character varying,
  lock_name character varying,
  lock_ref character varying,
  covered character varying,
  "lock:height" character varying,
  lock_namur character varying,
  access character varying,
  water character varying,
  ship character varying,
  old_name character varying,
  "ref:fgkz" character varying,
  level character varying,
  "source:geometry" character varying,
  "source:geometry:date" date,
  location character varying,
  "seamark:distance_mark:category" character varying,
  "seamark:distance_mark:distance" character varying,
  "seamark:distance_mark:units" character varying,
  leisure character varying,
  man_made character varying,
  ford character varying,
  tourism character varying,
  "river:waterway_distance" character varying,
  "seamark:bridge:category" character varying,
  "seamark:bridge:clearance_height" character varying,
  "seamark:bridge:clearance_width" character varying,
  "seamark:name" character varying,
  "OnroerendErfgoed:criteria" character varying,
  "addr:city" character varying,
  "addr:street" character varying,
  heritage character varying,
  "heritage:operator" character varying,
  "heritage:website" character varying,
  "ref:OnroerendErfgoed" character varying,
  "bridge:support" character varying,
  highway character varying,
  sloped_curb character varying,
  ft_symbol character varying,
  "waterway:sign" character varying,
  height character varying,
  image character varying,
  historic character varying,
  "artist:wikidata" character varying,
  artist_name character varying,
  artwork_type character varying,
  "source:geometry:entity" character varying,
  "source:geometry:oidn" character varying,
  "source:geometry:uidn" character varying,
  harbour character varying,
  phone character varying,
  port_of_entry character varying,
  "seamark:harbour:category" character varying,
  karst character varying,
  bicycle character varying,
  foot character varying,
  horse character varying,
  motor_vehicle character varying,
  seasonal character varying,
  railway character varying,
  leaf_cycle character varying,
  leaf_type character varying,
  CONSTRAINT "wfs.belgian_rivers_osm_20200402_pkey" PRIMARY KEY (gid)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE wfs.belgian_rivers_osm_20200402
  OWNER TO postgres;
GRANT ALL ON TABLE wfs.belgian_rivers_osm_20200402 TO postgres;
GRANT ALL ON TABLE wfs.belgian_rivers_osm_20200402 TO darwin2;

*/


--view to merge all osm rivers with the same name in one row
CREATE OR REPLACE VIEW wfs.v_belgian_rivers_osm_20200402_name_cluster AS 
 WITH a AS (
         SELECT belgian_rivers_osm_20200402.gid,
            belgian_rivers_osm_20200402.geom,
            belgian_rivers_osm_20200402.name,
            belgian_rivers_osm_20200402.id
           FROM wfs.belgian_rivers_osm_20200402
          ORDER BY belgian_rivers_osm_20200402.name
        ), b AS (
         SELECT b.gid,
            b.geom,
            b.name,
            a.gid AS neighbour
           FROM wfs.belgian_rivers_osm_20200402 b
             LEFT JOIN a ON st_intersects(b.geom, a.geom) AND a.gid <> b.gid AND a.gid > b.gid AND a.name::text = b.name::text
          ORDER BY b.name, b.gid
        ), c AS (
         SELECT b.gid,
            b.geom,
            b.name,
            b.neighbour,
            min(b.gid) OVER (PARTITION BY b.name) AS min
           FROM b
        ), d AS (
         SELECT c.min AS gid,
            c.min || array_agg(DISTINCT c.neighbour) AS cluster,
            c.name,
            st_union(c.geom) AS geom
           FROM c
          WHERE c.neighbour IS NOT NULL
          GROUP BY c.min, c.name
        ), e AS (
         SELECT c.gid,
            array_agg(DISTINCT c.neighbour) AS array_agg,
            c.name,
            c.geom
           FROM c
          WHERE c.neighbour IS NULL
          GROUP BY c.gid, c.name, c.geom
        )
 SELECT f.gid,
    f.cluster,
    f.name,
    f.geom
   FROM ( SELECT d.gid,
            d.cluster,
            d.name,
            d.geom
           FROM d
        UNION
         SELECT belgian_rivers_osm_20200402.gid,
            NULL::integer[],
            belgian_rivers_osm_20200402.name,
            st_multi(belgian_rivers_osm_20200402.geom) AS st_multi
           FROM wfs.belgian_rivers_osm_20200402
          WHERE NOT (belgian_rivers_osm_20200402.gid IN ( SELECT unnest(d.cluster) AS unnest
                   FROM d
                  WHERE d.cluster IS NOT NULL))) f
  ORDER BY f.name, f.gid;

ALTER TABLE wfs.v_belgian_rivers_osm_20200402_name_cluster
  OWNER TO darwin2;