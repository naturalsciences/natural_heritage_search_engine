# Franck Theeten 2020 04 04
#code heavily based on the QuickOSM pluging of Quantum GIS developped  by Etienne Trimaille

#use Osmium tool to merge the OSM files into a single file that can be converted into shapefile
#uses Python 3

import requests

save_folder="/YOUR_OUTPUT_FOLDER"

root_url="http://overpass-api.de/api/interpreter?data="
size_degree=4

#bounding box
x_min=12
x_max=32
y_min=-14
y_max=6

#osm_key
key="waterway"


cpt=1
#useful if download interrupted
cpt_min=1
for x in range(x_min,x_max, size_degree):
    print(x)
    for y in range(y_min,y_max, size_degree):
        if cpt>=cpt_min:
            cur_x_min=str(x)
            cur_x_max=x+size_degree
            if cur_x_max > x_max:
                cur_x_max=x_max
            cur_x_max=str(cur_x_max)

            cur_y_min=str(y)
            cur_y_max=y+size_degree
            if cur_y_max > y_max:
                cur_y_max=y_max
            cur_y_max=str(cur_y_max)
            cur_bbox=[cur_x_min, cur_y_min, cur_x_max, cur_y_max]
            print(cur_bbox)
            xml_query='<osm-script output="xml" timeout="25"><union><query type="node"><has-kv k="'+key+'"/><bbox-query s="'+cur_y_min+'" w="'+cur_x_min+'" n="'+cur_y_max+'" e="'+cur_x_max+'"/></query><query type="way"><has-kv k="'+key+'"/><bbox-query s="'+cur_y_min+'" w="'+cur_x_min+'" n="'+cur_y_max+'" e="'+cur_x_max+'"/></query><query type="relation"><has-kv k="'+key+'"/><bbox-query s="'+cur_y_min+'" w="'+cur_x_min+'" n="'+cur_y_max+'" e="'+cur_x_max+'"/></query></union><union><item/><recurse type="down"/></union><print mode="body"/></osm-script>'
            #print(xml_query)
            full_query=root_url+xml_query
            print(full_query)
            resp = requests.get(full_query)
            #print(resp.text)
            file=open(save_folder+'output_osm_'+str(cpt)+".osm", 'w', encoding="utf-8") 
            file.write(resp.text) 
            file.close()
        cpt=cpt+1
