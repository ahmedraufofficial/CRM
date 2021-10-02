import json 
'''

with open('map_contact.json', 'w') as f:
    data = {}
    data['map_contact'] = []
    json.dump(data, f)

with open('map_listing.json', 'w') as f:
    data = {}
    data['map_listing'] = []
    json.dump(data, f)


with open('contact_map.json','r+') as file:
    x = "oksa"
    y = "opas"
    columns = json.load(file)
    columns["contacts_map"].append({x:y})
    file.seek(0)
    json.dump(columns, file,indent=4)
    file.truncate()

'''
import csv

with open("listings.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        listings = []
        for row in reader:
                
               
                a = row
                listings.append(a[1:])
        for i in listings:
            print(i[1])
        print(len(listings))
            
        