#!/usr/bin/python

import json
import sys
import time
import datetime
#import Adafruit_DHT
import os
import mysql.connector
import smtplib

#import RPi.GPIO as GPIO
#from luma.led_matrix.device import max7219
#from luma.core.interface.serial import spi, noop
#from luma.core.virtual import viewport, sevensegment

# Install the following dependencies:
# sudo pip3 install Adafruit_DHT
# sudo apt-get install python3-mysql.connector

# Setup power relay
#GPIO.setmode(GPIO.BCM)
PWR = 26
#GPIO.setwarnings(False)
#GPIO.setup(PWR, GPIO.OUT)
RELAY_POWER = 'OFF'

# Setup sensor
#DHT_TYPE = Adafruit_DHT.AM2302
DHT_PIN = 14
FREQUENCY_SECONDS = 3

# Connect to the database
mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
cursor = mydb.cursor(buffered=True)

# Initialize the seven segment display
#serial = spi(port=0, device=0, gpio=noop())
#device = max7219(serial, cascaded=1)
#seg = sevensegment(device)

runningFlag = False

#SMTP Gmail Settings
gmail_user = 'email@gmail.com'
gmail_pwd = 'password'


def send_email(type, message, time):
    print("Attempting to send Email")
    cursor.execute("SELECT value FROM settings WHERE name = 'receiveEmail';")
    receive_email = cursor.fetchone()[0]
    if receive_email == '1':
        cursor.execute("SELECT value FROM settings WHERE name = 'email';")
        to_email = cursor.fetchone()[0]
        if to_email is not None:
            to = to_email
            try:
                smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
                smtpserver.ehlo()
                smtpserver.starttls()
                smtpserver.ehlo
                smtpserver.login(gmail_user, gmail_pwd)
                header = 'To:' + to + '\n'\
                         + 'From: ' + gmail_user + '\n'\
                         + 'Subject: ' + message + '\n'
                # print header
                msg = header + '\n' + message + '\n at ' + time + '.\n\n'
                # print msg
                smtpserver.sendmail(gmail_user, to, msg)
                smtpserver.close()
                print("Email Sent")
            except:
                print("Error sending Email")


def waiting(runningFlag):
    while not runningFlag:
        print("Waiting...")
        cursor.execute("SELECT temperature, humidity FROM configurations WHERE running = 1;")
        current = cursor.fetchone()

        if (current is None):
            print("No running configuration found. Waiting.")
            time.sleep(2)
        else:
            print("Starting running...")
            runningFlag = True
            running(runningFlag)

            mydb.commit()


def running(runningFlag):
    while runningFlag:
        os.system('clear')
        print("Smart Incubator")
        # connect to database
        # find running config
        print("Retrieving configuration...")
        cursor.execute("SELECT temperature, humidity FROM configurations WHERE running = 1;")
        current = cursor.fetchone()
        print(current)
        if current is None:
            print("No running configuration found. Return to wait")
            runningFlag = False;
            waiting(runningFlag)
        else:
            print("Configuration loaded.")

            temperatureThreshold = current[0]
            humidityThreshold = current[1]

            # Attempt to get the sensor readings
            print("Retrieving sensor readings...")
            #humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
            humidity =20
            temp = 28

            # Skip to the next reading if a valid measurement couldn't be taken.
            # This might happen if the CPU is under a lot of load and the sensor can't be reliably read.
            if humidity is None or temp is None:
                print("No humidity or temperature data returned. Retrying in 2 seconds.")
                time.sleep(2)
                continue

            # Print to seven-digit display
  #          seg.text = "{0:0.1f} C".format(temp)
   #         time.sleep(3)
    #        seg.text = "H {0:0.1f}".format(humidity)

            # Check the sensor readings
            print("Sensor data found. Processing...")
            if temp > int(temperatureThreshold):
                #GPIO.output(PWR, False)
                RELAY_POWER = 'OFF'
            elif temp <= int(temperatureThreshold):
                #GPIO.output(PWR, True)
                RELAY_POWER = 'ON'

                # Check if temperature notification needs to be sent
            cursor.execute("SELECT MAX(timestamp) as timestamp,title FROM notifications WHERE title = 'Temperature';")
            latestTemperatureNotificationTime = cursor.fetchone()
            if latestTemperatureNotificationTime[0] is None:
                latestTemperatureNotificationTime = (datetime.datetime(2000, 1, 1), "Temperature")

            if datetime.datetime.now() >= latestTemperatureNotificationTime[0] + datetime.timedelta(hours=1):
                if temp > int(temperatureThreshold) + 3:
                    print("Inserting temperature notification into the database...")
                    query = "INSERT INTO notifications(title,text,type) VALUES(%s,%s,%s)"
                    cursor.execute(query, ("Temperature", "Incubator temperature is {:.1f}  degrees C".format(temp), "error"))
                    mydb.commit()
                    print("Temperature greater than threshold Notification Created");
                    send_email("Temperature", "Incubator temperature is {:.1f} degrees C".format(temp), datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

                elif temp <= int(temperatureThreshold) - 3:
                    print("Inserting temperature notification into the database...")
                    query = "INSERT INTO notifications(title,text,type) VALUES(%s,%s,%s)"
                    cursor.execute(query, ("Temperature", "Incubator temperature is {:.1f} degrees C".format(temp), "error"))
                    mydb.commit()
                    print("Temperature less than threshold Notification Created");
                    send_email("Temperature", "Incubator temperature is {:.1f} degrees C".format(temp), datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

            # Check if humidity notification needs to be sent
            cursor.execute("SELECT MAX(timestamp) as timestamp,title FROM notifications WHERE title = 'Humidity';")
            latestHumidityNotificationTime = cursor.fetchone()
            if latestHumidityNotificationTime[0] is None:
                latestHumidityNotificationTime = (datetime.datetime(2000, 1, 1), "Humidity")

            if datetime.datetime.now() >= latestHumidityNotificationTime[0] + datetime.timedelta(hours=1):
                if humidity > int(humidityThreshold) + 3:
                    print("Inserting humidity notification into the database...")
                    query = "INSERT INTO notifications(title,text,type) VALUES(%s,%s,%s)"
                    cursor.execute(query, ("Humidity", "Incubator humidity is {:.1f} %".format(humidity), "error"))
                    mydb.commit()
                    print("Humidity greater than threshold Notification Created");
                    send_email("Humidity", "Incubator humidity is {:.1f} %".format(humidity), datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                elif humidity <= int(humidityThreshold) - 3:
                    print("Inserting humidity notification into the database...")
                    query = "INSERT INTO notifications(title,text,type) VALUES(%s,%s,%s)"
                    cursor.execute(query, ("Humidity", "Incubator humidity is {:.1f} %".format(humidity), "error"))
                    mydb.commit()
                    print("Humidity less than threshold Notification Created");
                    send_email("Humidity", "Incubator humidity is {:.1f} %".format(humidity), datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

            # Print the current readings
            # os.system('clear')
            print('Temperature: {0:0.1f} C'.format(temp))
            print('Humidity:    {0:0.1f} %'.format(humidity))
            print('Relay Power: {0}'.format(RELAY_POWER))
            print('Press Ctrl-C to quit.')

            # Add the readings to the database
            print("Inserting data into the database...")
            query = "INSERT INTO incubator(temperature,humidity,power) VALUES(%s,%s,%s)"
            cursor.execute(query, ('{0:0.1f}'.format(temp), '{0:0.1f}'.format(humidity), RELAY_POWER))
            mydb.commit()

            # delete readings in database that are over 24 hours old
            print("Deleting data in the database that is older than 24 hours...")
            query = "DELETE FROM incubator WHERE timestamp < NOW() - INTERVAL 1 DAY"
            cursor.execute(query)
            mydb.commit()

            # Wait before continuing
            time.sleep(FREQUENCY_SECONDS)


waiting(runningFlag)
