import pandas as pd

cols_obj={}
results={}
src_excel="C:\\Users\\ftheeten\\Downloads\\passport_identification_export_url.xlsx"

def add_or_concatenate_key(row, institution, pos, field):
    global results
    if not pd.isna(row[pos]):
        existing=""
        if field in results[institution]:            
            existing=results[institution][field]
            print("EXISTING "+field + " in "+institution+"="+existing)
            existing=existing+"\r\n"+row[pos]
        else:
            print("NEW "+field + " in "+institution+"="+str(row[pos]))
            existing=row[pos]
        results[institution].update({field:str(existing).strip()})

def parse(excel):
    global results
    print(excel)
    ex_data = pd.read_excel(excel)
    headers=ex_data.head()
    current_inst=""
    i=0
    for cols in ex_data.columns:
        print(cols)
        cols_obj.update({i:cols})
        i+=1
    for i, row in ex_data.iterrows():
        print(i)
        if not pd.isna(row[0]):
            current_inst=row[0]
            results.update({current_inst:{}})
        print(current_inst)
        
        results[current_inst].update({'name':current_inst})
        for key, col_name in cols_obj.items():
              print(key)
              print(col_name)
              print(row[key])
              add_or_concatenate_key(row, current_inst, key, col_name)
    print(results)

if __name__ == "__main__":
    parse(src_excel)