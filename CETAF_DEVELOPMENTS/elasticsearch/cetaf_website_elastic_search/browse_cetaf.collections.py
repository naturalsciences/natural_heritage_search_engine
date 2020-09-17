import pandas as pd
import csv
cols_obj={}
results={}
src_excel="C:\\Users\\ftheeten\\Downloads\\passport-collection_work_earth.xlsm"
dest="C:\\Users\\ftheeten\\Downloads\\passport-collection_work_earth.txt"


def parse(excel, p_dest):
    global results
    global cols_obj
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
            #results.update({current_inst:{}})
        print(current_inst)
        if not pd.isna(row[2]):
            results[current_inst+'/'+str(i)]={}
            #results[current_inst].update({'name':current_inst})
            for key, col_name in cols_obj.items():
                  print(key)
                  print(col_name)
                  print(row[key])
                  val=""
                  if not pd.isna(row[key]):
                     val=str(row[key])
                  results[current_inst+'/'+str(i)].update({col_name:val.strip()})
                  #add_or_concatenate_key(row, current_inst, key, col_name)
            results[current_inst+'/'+str(i)].update({"institution":current_inst})
    print(results)
    with open(p_dest, 'w' , encoding="utf-8",newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(cols_obj.values()), delimiter='\t')
        writer.writeheader()
        for val in results.items():
            print(val[1])
            writer.writerow(val[1])

if __name__ == "__main__":
    parse(src_excel,dest)