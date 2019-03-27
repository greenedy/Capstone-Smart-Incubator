import mysql.connector
import Adafruit_DHT
import os
import sys
import time
import RPi.GPIO as GPIO
from scripts.incubator import configuration
from scripts.incubator import incubator


class runningConfiguration():

    def __init__(self, configuration):

        self.configuration = configuration
        self.incubator = incubator

        # Setup the relay connection
        GPIO.setmode(GPIO.BCM)
        self.PWR = 26
        GPIO.setwarnings(False)
        GPIO.setup(self.PWR,GPIO.OUT)

        # Type of sensor
        self.DHT_TYPE = Adafruit_DHT.AM2302

        # Example of sensor connected to Raspberry Pi pin 23
        self.DHT_PIN  = 4

        # Set the power state of the relay
        self.RELAY_POWER = 'OFF'

def main():

    runConfig = runningConfiguration()

    while runConfig.configuration.run:

        # Attempt to get sensor reading.
        humidity, temperature = Adafruit_DHT.read(runConfig.DHT_TYPE, runConfig.DHT_PIN)

        # Skip to the next reading if a valid measurement couldn't be taken.
        # This might happen if the CPU is under a lot of load and the sensor
        # can't be reliably read (timing is critical to read the sensor).
        if humidity is None or temperature is None:
            time.sleep(2)
            continue

        if (temperature > runConfig.configuration.temperature):
            GPIO.output(runConfig.PWR, False)
            RELAY_POWER = 'OFF'
        elif (temperature < runConfig.configuration.temperature):
            GPIO.output(runConfig.PWR, True)
            RELAY_POWER = 'ON'

        print("Smart Incubator")
        try:
            incubator.addTemperatureHumidityToDatabase(humidity, temperature)

        except:
            time.sleep(runConfig.configuration.frequency)
            continue

        # Wait before continuing
        time.sleep(runConfig.configuration.frequency)
