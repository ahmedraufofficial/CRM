text = "Conference Room,Covered Parking,Available Furnished,Availabe Networked,Shared Gym,Shared Spa,Dining in Building,Retail in Building,View of Water,View of Landmark"
text="Maids Room,Study,Central A/C & Heating,Balcony,Private Garden,Private Pool,Private Gym,Private Jacuzzi,Shared Pool,Shared Spa,Shared Gym,Security,Concierge Service,Maid Service,Covered Parking,Built in Wardrobes,Walk-in Closet,Built in Kitchen Appliances,View of Water,View of Landmark,Pets Allowed"
s = text.split(',')

#for i in s:
#    print('"'+i+'":"'+i+'",')

text = "sd,sa,dsa"

ame = lambda T:"|".join(T.split(","))

#print(ame(text))



a = "Status,Employee Status,Employee ID,Name,Position,Nationality,UID,Date of Birth,Date of Joining,Emirates ID,Card No,Emirates Card Expiry,Mobile No,MOL Personal No,Labor Card No,Labor Card Expiry,Insurance No,Insurance Effective Date,Insurance Expiry Date,Date of Submission,Residence Expiry,Remarks"

all = a.split(",")

for i in all:
    print('{'+'"field":"'+i.replace(" ","_")+'","title":"' +i+'","sortable":"True"},')

