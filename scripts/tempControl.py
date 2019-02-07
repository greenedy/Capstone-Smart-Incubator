#!/usr/bin/python

import json
import sys
import time
import datetime
import Adafruit_DHT
import mysql.connector
import gspread
import os
import MySQLdb
import RPi.GPIO as GPIO
from oauth2client.service_account import ServiceAccountCredentials

# Setup the relay connection
GPIO.setmode(GPIO.BCM)
PWR = 26
GPIO.setwarnings(False)
GPIO.setup(PWR,GPIO.OUT)

# Start the camera server
os.system('sudo service motion restart')

# Connect to the database
conn = MySQLdb.connect(host= "localhost", user="root", passwd="klcmc123", db="mydb")
x = conn.cursor()

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.AM2302

# Example of sensor connected to Raspberry Pi pin 23
DHT_PIN  = 4

# Set the Google credentials file
GDOCS_OAUTH_JSON	= 'pincubator-203201-0c9d734cc242.json'

# Google Docs spreadsheet name.
GDOCS_SPREADSHEET_NAME	= 'DHT Humidity Logs'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS	= 3

# Set the power state of the relay
RELAY_POWER		= 'OFF'

def login_open_sheet(oauth_key_file, spreadsheet):
    """Connect to Google Docs spreadsheet and return the first worksheet."""
    try:
        scope =  ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except Exception as ex:
        print('Unable to login and get spreadsheet.  Check OAuth credentials, spreadsheet name, and make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
        print('Google sheet login failed with error:', ex)
        sys.exit(1)

worksheet = None
while True:
    # Login if necessary.
    if worksheet is None:
        worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)

    # Attempt to get sensor reading.
    humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

    # Skip to the next reading if a valid measurement couldn't be taken.
    # This might happen if the CPU is under a lot of load and the sensor
    # can't be reliably read (timing is critical to read the sensor).
    if humidity is None or temp is None:
        time.sleep(2)
        continue

    if (temp > 38.0):
        GPIO.output(PWR, False)
        RELAY_POWER = 'OFF'
    elif (temp < 37.0):
        GPIO.output(PWR, True)
        RELAY_POWER = 'ON'

    os.system('clear')
    print('Temperature: {0:0.1f} C'.format(temp))
    print('Humidity:    {0:0.1f} %'.format(humidity))
    print('Relay Power: {0}'.format(RELAY_POWER))
    print('Logging sensor readings to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS))
    print('Press Ctrl-C to quit.')

    # Append the data in the spreadsheet, including a timestamp
    try:
        worksheet.delete_row(2)
        worksheet.append_row([temp, humidity])
        x.execute("""INSERT INTO incubator VALUES (%s,%s, NOW())""",(temp,humidity))
        conn.commit()
    except:
        # Error appending data, most likely because credentials are stale.
        # Null out the worksheet so a login is performed at the top of the loop.
        print('Append error, logging in again')
        worksheet = None
        conn.rollback()
        time.sleep(FREQUENCY_SECONDS)
        continue

    # Wait before continuing
time.sleep(FREQUENCY_SECONDS)