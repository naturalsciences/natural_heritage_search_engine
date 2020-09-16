import requests, json, csv

size=500
offset=0
page=0
url="https://api.gbif.org/v1/grscicoll/institution"
dict=[]
save_file = "grscicoll_inst.txt"


def get_results(json):
    global dict
    results=json["results"]
    key=0
    for item in results:
        address=""
        if "address" in item:
            address= '; '.join(str(v) for v in item["address"].values() )   
        dict.append({"institution_name":item["name"], "grscicoll_code":item["code"], "address": address })
        
def parse(p_url, p_file, csv_columns):
    global size, offset, page, dict
    endOfRecords=False
    while not endOfRecords:
        paged_url=p_url+"?limit="+str(size)+"&offset="+str(offset)
        print(paged_url)
        response = requests.get(paged_url)
        data = response.json()
        get_results(data)
        #print(data)
        #print(data["endOfRecords"])
        endOfRecords=data["endOfRecords"]
        page=page+1
        #print(page)
        offset=page*size
    print(dict)
    with open(p_file, 'w', encoding="utf-8",newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter='\t')
        writer.writeheader()
        for data in dict:
            writer.writerow(data)
        
        
if __name__ == "__main__":
    parse(url, save_file, ["institution_name", "grscicoll_code", "address"])