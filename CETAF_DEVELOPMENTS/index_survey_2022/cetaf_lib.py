def flatten(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])

def get_value(row, dict_mars):
    returned = None
    source=dict_mars[row['field']]
    if not source is None:
        source=remove_html(source)
        if 'es_use_field_name_in_data' in row:
            if len(row['es_use_field_name_in_data'].strip())>0:
                source= row['es_use_field_name_in_data']+": "+str(source)
        #if 'es_prefix' in row:
        #    if len(row['es_prefix'].strip())>0:
        #        source= row['es_prefix']+": "+str(source)       
        if isinstance(source, list):
            go_flat=True
            if "es_keep_list" in row:
                if row["es_keep_list"].lower().strip()=="yes":
                    go_flat=False
            source=flatten(source)            
            if go_flat is True:                
                source='; '.join(source)            
        elif isinstance(source, dict):
            if "download" in source:
                source=source["download"]
        print(source)
        #if len(source.strip())>0:
            #if isinstance(source, list):
            #    source=flatten(source)
        if isinstance(source, str):
            if len(source.strip())>0:
                returned=source.strip()
        else:
            returned=source
    return returned   