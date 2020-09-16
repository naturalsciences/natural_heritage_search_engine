import pandas as pd
import csv

cols_obj={}
results={}
src_excel="passport_identification_export_url.xlsx"
save_file = "cetaf_inst.txt"

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

def parse(excel,p_file):
    global results
    print(excel)
    csv_columns=[]
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
        if not pd.isna(row[1]):
            current_inst=row[1]
            results.update({current_inst:{}})
        print(current_inst)
        
        results[current_inst].update({'Name':current_inst})
        for key, col_name in cols_obj.items():
              print("key="+str(key))
              print(col_name)
              print(row[key])
              if i==0:
                  csv_columns.append(col_name)
              add_or_concatenate_key(row, current_inst, key, col_name)
    #print(results)
    print(csv_columns)    
    with open(p_file, 'w', encoding="utf-8",newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter='\t')
        writer.writeheader()
        for val in results.items():
            print(val[1])
            writer.writerow(val[1])
            

if __name__ == "__main__":
    parse(src_excel, save_file)