import mysql.connector
import Adafruit_DHT
import os
import sys
import time
import RPi.GPIO as GPIO

# Setup the relay connection
GPIO.setmode(GPIO.BCM)
PWR = 26
GPIO.setwarnings(False)
GPIO.setup(PWR,GPIO.OUT)

# Type of sensor
DHT_TYPE = Adafruit_DHT.AM2302

# Example of sensor connected to Raspberry Pi pin 23
DHT_PIN  = 4

# Connect to database
mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")

mycursor = mydb.cursor()

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS = 3

# Set the power state of the relay
RELAY_POWER = 'OFF'

while True:

    # Attempt to get sensor reading.
    humidity, temperature = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

    # Skip to the next reading if a valid measurement couldn't be taken.
    # This might happen if the CPU is under a lot of load and the sensor
    # can't be reliably read (timing is critical to read the sensor).
    if humidity is None or temperature is None:
        time.sleep(2)
        continue

    if (temperature > 38.0):
        GPIO.output(PWR, False)
        RELAY_POWER = 'OFF'
    elif (temperature < 37.0):
        GPIO.output(PWR, True)
        RELAY_POWER = 'ON'

    print("Smart Incubator")
    try:

        sql = "INSERT INTO incubator (humidity, temperature) VALUES (%s, %s)"
        val = (humidity, temperature)
        mycursor.execute(sql, val)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")

    except:
        time.sleep(FREQUENCY_SECONDS)
        continue

    # Wait before continuing
    time.sleep(FREQUENCY_SECONDS)