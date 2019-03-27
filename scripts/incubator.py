from scripts.database import database
import  time


class incubator():

    def __init__(self):
        self.configuration = configuration()
        self.run = False
        self.db = database()

    def addTemperatureHumidityToDatabase(self, temperature, humidity):
        sql = "INSERT INTO incubator (humidity, temperature) VALUES (%s, %s)"
        val = (humidity, temperature)
        self.db.query(sql, val)

    def addNotificationToDatabase(self, text):
        sql = "INSERT INTO notifications (title, text, type) VALUES (%s, %s)"
        val = (text, text, "Error")
        self.db.query(sql, val)

    def startConfig(self):
        self.configuration.startRunning()

    def stopConfig(self):
        self.configuration.stopRunning()

    def setConfiguration(self, temperature, humidity, frequency, duration):
        self.configuration.setTemperature(temperature)
        self.configuration.setHumidity(humidity)
        self.configuration.setFrequency(frequency)
        self.configuration.setDuration(duration)


class configuration():

    def setTemperature(self, temperature):
        self.temperature = temperature

    def setHumidity(self, humidity):
        self.humidity = humidity

    def setFrequency(self, frequency):
        self.frequency = frequency

    def setDuration(self, duration):
        self.duration = duration

    def startRunning(self):
        self.run = True

    def stopRunning(self):
        self.run = False