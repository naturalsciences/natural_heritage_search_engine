from bs4 import BeautifulSoup
import re

def cast_to_numeric(val):
    tmp=0
    if isinstance(val,str):
        if len(val.strip)>0:
            tmp=re.sub("[^0-9.,]", "", val)
            tmp=tmp.replace(",",".")
    elif isinstance(val,(int, float, complex)):
        return val
    return tmp

def cast_to_int(val):
    tmp=cast_to_numeric(val)
    return int(round(float(tmp),0))

def get_value_field(p_dict, field):
    returned = None
    source=p_dict[field]
    if not source is None:
        source=remove_html(source)
        if isinstance(source, list):
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


def remove_html(dict_var):
    returned=dict_var
    list_data=None
    table_data=None
    table_data_set=False
    if  isinstance(dict_var,dict):
        if "content-type" in dict_var and "data" in dict_var:
            if dict_var["content-type"]=="text/html":
                print("IS_HTML")
                print(dict_var["data"])
                go_parse_table=False
                go_find_item=False
                if BeautifulSoup(dict_var["data"]).find("div", {"class": "field-item"}):
                    go_find_item=True
                    list_items=BeautifulSoup(dict_var["data"]).find_all("div", {"class": "field-item"})
                    list_data=[]
                    for item_row in list_items:
                        list_data.append(item_row.text.replace('\xa0', ' ').strip())
                elif BeautifulSoup(dict_var["data"]).find("tr"):
                    if BeautifulSoup(dict_var["data"]).find("td"):
                        go_parse_table=True
                if go_find_item is True:
                    returned=list_data
                elif go_parse_table:
                    table_data = [[cell.text.replace('\xa0', ' ').strip() for cell in row("td")]
                                                     for row in BeautifulSoup(dict_var["data"])("tr")]
                    table_data_set=True
                else:
                    table_data=dict_var["data"]
                    table_data_set=True
                if table_data_set is True:
                    if table_data==[['']]:
                        print("TABLE_1")
                        returned=[]
                    else:
                        print("TABLE_2")
                        returned=table_data
                        print(returned)
    return returned
    