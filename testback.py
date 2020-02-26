"""
Example for using the RFM69HCW Radio with Raspberry Pi.

Learn Guide: https://learn.adafruit.com/lora-and-lorawan-for-raspberry-pi
Author: Brent Rubell for Adafruit Industries
"""
# Import Python System Libraries
import time
# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import the RFM69 radio module.
import adafruit_rfm69
# firebase imports
import datetime
from firebase import firebase
import json
import pyowm
import os
import urllib
from geopy.geocoders import Nominatim
from functools import partial

################### farmly globals
twoplants = True
moist2 = 123
plant2 = "Carrot"
user = "alan"
plant = "Tomato"
city = 'Austin, Texas'
moisture = 3421
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
#################

# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
#btnC.direction = Direction.INPUT
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Configure Packet Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm69 = adafruit_rfm69.RFM69(spi, CS, RESET, 915.0)
prev_packet = None
# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm69.encryption_key = b'\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08'



while True:
    packet = None
    # draw a box to clear the image
    display.fill(0)
    display.text('RasPi Radio', 35, 0, 1)

    # check for packet rx
    packet = rfm69.receive()
    if packet is None:
        display.show()
        display.text('- Waiting for PKT -', 15, 20, 1)
    else:
        # Display the packet text and rssi
        display.fill(0)
        prev_packet = packet
       # print(int(str(prev_packet,"utf-8")))
       # print(moisture)
        packet_text = str(prev_packet, "utf-8")

        display.text('RX: ', 0, 0, 1)
        display.text(packet_text, 25, 0, 1)
        ##########################################
        ts = str(datetime.datetime.now())
        timestamp = ts[:19]
        replaced = timestamp.replace(" ", " ")
        print(replaced) 
        data = {"temp": temp["temp"] , "plant_moisture": packet_text, "humidity": humidity, "rainfall": lastrain, "sunlight": sunlight}

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
           data2 = {"temp": temp["temp"] , "plant_moisture": moist2, "humidity": humidity, "rainfall": lastrain, "sunlight":sunlight}
           print(data2)
           firebase.put(putLoc2,plant2, data2)
           print("Second POST Success")
        #########################################
        display.show()
        time.sleep(30)

