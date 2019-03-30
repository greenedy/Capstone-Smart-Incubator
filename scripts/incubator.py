#!/usr/bin/python

import json
import sys
import time
import datetime
import Adafruit_DHT
import os
import mysql.connector
import RPi.GPIO as GPIO

# Install the following dependencies:
# sudo pip3 install Adafruit_DHT
# sudo apt-get install python3-mysql.connector

# Setup power relay
GPIO.setmode(GPIO.BCM)
PWR = 26
GPIO.setwarnings(False)
GPIO.setup(PWR, GPIO.OUT)
RELAY_POWER = 'OFF'

# Setup sensor
DHT_TYPE = Adafruit_DHT.AM2302
DHT_PIN = 14
FREQUENCY_SECONDS = 3

# Connect to the database
mydb = mysql.connector.connect(host="localhost", user="pi", passwd="klcmc123", database="smartincubator")
cursor = mydb.cursor(buffered=True)

running = True;
while running:
    os.system('clear')
    print("Smart Incubator")
    # connect to database
    # find running config
    print("Retrieving configuration...")
    cursor.execute("SELECT temperature, humidity FROM configurations WHERE running = 1;")
    current = cursor.fetchone()
    temperatureThreshold = current[0]
    humidityThreshold = current[1]

    if (len(current) == 0):
        print("No running configuration found. Aborting.")
        running = False;
        break;
    print("Configuration loaded.")

    # Attempt to get the sensor readings
    print("Retrieving sensor readings...")
    humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

    # Skip to the next reading if a valid measurement couldn't be taken.
    # This might happen if the CPU is under a lot of load and the sensor can't be reliably read.
    if humidity is None or temp is None:
        print("No humidity or temperature data returned. Retrying in 2 seconds.")
        time.sleep(2)
        continue

    # Check the sensor readings
    print("Sensor data found. Processing...")
    if (temp > int(temperatureThreshold)):
        GPIO.output(PWR, False)
        RELAY_POWER = 'OFF'
    elif (temp <= int(temperatureThreshold)):
        GPIO.output(PWR, True)
        RELAY_POWER = 'ON'

    # Check if temperature notification needs to be sent
    if (temp > int(temperatureThreshold) + 3):
        print("Inserting temperature notification into the database...")
        query = "INSERT INTO notifications(title,text,type) VALUES(%s,%s,%s)"
        cursor.execute(query, ("Incubator temperature is " + str(temp) + " °C", "Incubator temperature is " + str(temp) + " °C", "error"))
        mydb.commit()
    elif (temp <= int(temperatureThreshold) - 3):
        print("Inserting temperature notification into the database...")
        query = "INSERT INTO notifications(title,text,type) VALUES(%s,%s,%s)"
        cursor.execute(query, ("Incubator temperature is " + str(temp) + " °C", "Incubator temperature is " + str(temp) + " °C", "error"))
        mydb.commit()

    # Check if humidity notification needs to be sent
    if (humidity > int(humidityThreshold) + 3):
        print("Inserting humidity notification into the database...")
        query = "INSERT INTO notifications(title,text,type) VALUES(%s,%s,%s)"
        cursor.execute(query, ("Incubator humidity is " + str(humidity) + " %", "Incubator humidity is " + str(humidity) + " %", "error"))
        mydb.commit()
    elif (humidity <= int(humidityThreshold) - 3):
        print("Inserting humidity notification into the database...")
        query = "INSERT INTO notifications(title,text,type) VALUES(%s,%s,%s)"
        cursor.execute(query, ("Incubator humidity is " + str(humidity) + " %", "Incubator humidity is " + str(humidity) + " %", "error"))
        mydb.commit()

    # Print the current readings
    # os.system('clear')
    print('Temperature: {0:0.1f} C'.format(temp))
    print('Humidity:    {0:0.1f} %'.format(humidity))
    print('Relay Power: {0}'.format(RELAY_POWER))
    print('Press Ctrl-C to quit.')

    # Add the readings to the database
    print("Inserting data into the database...")
    query = "INSERT INTO incubator(temperature,humidity,power) VALUES(%s,%s,%s)"
    cursor.execute(query, (temp, humidity, RELAY_POWER))
    mydb.commit()

    # Wait before continuing
    time.sleep(FREQUENCY_SECONDS)