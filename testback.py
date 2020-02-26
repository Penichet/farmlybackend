import time
import datetime
from firebase import firebase
import json
import pyowm
import os
import urllib
from geopy.geocoders import Nominatim
from functools import partial
########## VALUES ##############
twoplants = True
moist2 = 123
plant2 = "Carrot"
user = "alan"
plant = "Tomato"
city = 'Austin, Texas'
moisture = 42
################################
fburl = 'https://farmlybackend.firebaseio.com'
weatherkey = 'c20e9a80a1d0540720c98726c6658619'
################################
geolocator = Nominatim(user_agent="FarmlyDevice")
print(city)
location = geolocator.geocode(city)
lat = location.latitude
long = location.longitude
################################
# acquire endpoints
firebase = firebase.FirebaseApplication(fburl)
owm = pyowm.OWM(weatherkey)
# Load up data
location = owm.weather_at_coords(lat,long)
localweather = location.get_weather()
uvi = owm.uvindex_around_coords(lat,long)
if(localweather): print("Weather get success from " + city)
# Weather api
sunlight = uvi.get_value()
humidity = localweather.get_humidity()
temp = localweather.get_temperature()
rain = localweather.get_rain()
if len(rain) == 0:
	lastrain = 0
else: 
	#print rain
	lastrain = rain["1h"]
#####################
ts = str(datetime.datetime.now())
timestamp = ts[:19]
replaced = timestamp.replace(" ", " ")
print(replaced)
# Create Data table
data = {"temp": temp["temp"] , "plant_moisture": moisture, "humidity": humidity,
	 "rainfall": lastrain, "sunlight": sunlight} 
#data = "randomshit"
print(data)
#nesting shit
#plantnest = {plant : values}
#data = {replaced : plantnest}
# POST
putLoc = '/' + user + '/' +  replaced
#putLoc = '/' + user + '/'
#putLoc = '/functions/update'
#print data
print("adding to" + putLoc)

#firebase.post(putLoc, data)
firebase.put(putLoc, plant, data)
print("PUT succeeded at " + putLoc)

if(twoplants):
	putLoc2  = '/' + user + '/' + replaced 
	data2 = {"temp": temp["temp"] , "plant_moisture": moist2, "humidity": humidity,
		"rainfall": lastrain, "sunlight":sunlight}	
	print(data2)	
	firebase.put(putLoc2,plant2, data2)
	print("Second POST Success")
