text = "Conference Room,Covered Parking,Available Furnished,Availabe Networked,Shared Gym,Shared Spa,Dining in Building,Retail in Building,View of Water,View of Landmark"
text="Maids Room,Study,Central A/C & Heating,Balcony,Private Garden,Private Pool,Private Gym,Private Jacuzzi,Shared Pool,Shared Spa,Shared Gym,Security,Concierge Service,Maid Service,Covered Parking,Built in Wardrobes,Walk-in Closet,Built in Kitchen Appliances,View of Water,View of Landmark,Pets Allowed"
s = text.split(',')

#for i in s:
#    print('"'+i+'":"'+i+'",')

text = "sd,sa,dsa"

ame = lambda T:"|".join(T.split(","))

print(ame(text))

