import wikipedia
import pandas as pd
import re
import hashlib
import os

#Remove links if any and fill in country eg "Vatican City" -> "Vatican City, Vatican City"
def prep_loc(col):
    col=re.sub("[\[].*?[\]]", "", col)
    if ',' not in col:
       col=col+', '+col

    #exceptions 
    if col.startswith("Hong Kong"):
       col="Hong Kong, Hong Kong"
    
    elif col.startswith("New York City"):
       col="New York, United States"

    return col

#Convert values like "7,726,321[1][2]" to int "7726321" - remove links and commas
def prep_int(col):  
    return re.sub("[\[].*?[\]]", "", col).replace(',','') 

#Remove links eg "Opium War Museum [zh]"
def prep_str(col):
    return re.sub("[\[].*?[\]]", "", col)

def get_museums_data(page):
   
	#NOTE: Open issue with wikipedia related to reading tables https://github.com/goldsmith/Wikipedia/issues/111 

	#Extract data from Wikipedia page
	#NOTE: Data from 2022
	top_museums=pd.read_html(wikipedia.page(page).html())[0]

	#NOTE: This works as well 
	#top_museums=pd.read_html("https://en.wikipedia.org/wiki/" + page, attrs={"class":"wikitable"})[0]

	#Fix header
	top_museums.rename(columns={'Visitors in 2022':'visitors'}, inplace=True)
	top_museums.columns=top_museums.columns.str.lower()

	#TODO: Data checks

	#NOTE: Location also contains single city name without country "Vatican City" - exception; in this case country name is also "Vatican City",
	#need to transform to "Vatican City, Vatican City"

	#Cleanup data 
	top_museums.name=top_museums.name.apply(prep_str)
	top_museums.location=top_museums.location.apply(prep_loc)
	top_museums.visitors=pd.to_numeric(top_museums.visitors.apply(prep_int))

	#Only include museums with >2000000 visitors? 
	#print(top_museums.loc[top_museums.Visitors>2000000]) - only 27

	return top_museums

def get_cities_population(file):

    #NOTE: Data from 2023: https://simplemaps.com/data/world-cities
    cities = pd.read_csv(file, usecols=["city", "country", "admin_name", "population"], dtype={"population" : "Int32"})

    #Exception in data 
    cities.loc[(cities['city'] == "Washington") & (cities['admin_name'] == "District of Columbia"),'city']="Washington, D.C."

    #Location contains value like "Washington, D.C., United States" => can't split by "," into city, country => need to merge to compare
    cities["location"]=cities["city"] + ', ' + cities["country"]
    cities.drop(["city", "country", "admin_name"], axis=1, inplace=True)

    return cities 

def get_cities_density(file, cities):

    density = pd.read_csv(file, sep="\t", dtype={"density" : "Int32"})

    #merge tables, keep original sorting order 
    cities=pd.merge(cities, density, on=["location"], how="left")

    return cities

def gen_id(text):
    return int(hashlib.sha512(text.encode('utf-8')).hexdigest(), 16)%(10**8)

def create_db(museums, cities): 
    #merge tables, keep original sorting order by visitors
    museums_db=pd.merge(museums, cities, on=["location"], how="left")

    #Cities data contains duplicate cities in different provinces in China
    #We don't have enough data to resolve this ambiguity => lets assume that city with larger population is the one we need
    #Examples: Dongguan, China; Suzhou, China 
    museums_db = museums_db.sort_values(by='population', ascending=False)
    museums_db = museums_db.drop_duplicates(subset='name', keep="first")
    museums_db = museums_db.sort_values(by='visitors', ascending=False)

    museums_db.insert(0, "rank", range(1,len(museums_db)+1)) 
    museums_db["id"]=(museums_db.name + museums_db.location).apply(gen_id)

    return museums_db 

def generate_db():
    module_dir = os.path.dirname(os.path.abspath(__file__))

    top_museums=get_museums_data("List_of_most-visited_museums")
    cities=get_cities_population(os.path.join(module_dir,"../external/worldcities.csv"))
    cities=get_cities_density(os.path.join(module_dir, "../external/location_density_google.csv"), cities)

    top_museums_db=create_db(top_museums, cities) 
    assert len(top_museums_db)==len(top_museums), "Error: some locations were not found!"

    top_museums_db.to_csv(os.path.join(module_dir,"../db/top_museums.csv"), sep="\t", index=False)

if __name__ == '__main__':
   	generate_db()
 
     