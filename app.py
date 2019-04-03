
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, jsonify
from passlib.hash import sha256_crypt
#from scripts import incubator
import mysql.connector
import datetime
import os
import subprocess
import psutil

app = Flask(__name__)


# Empty URL redirects to the login page if not logged in or dashboard if already logged in
@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))
    else:
        return redirect(url_for('dashboard_load'))


# The register url loads the register html page
# Register page allows user to create username and password
@app.route('/register')
def register_load():
    if not session.get('logged_in'):
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("SELECT * from users")
        if cursor.rowcount != 0:
            return redirect(url_for('login_load'))
        else:
            return render_template('register.html')
    else:
        return redirect(url_for('dashboard_load'))


# Username and Password are sent to database
# Password is encrypted
@app.route('/register', methods=['POST'])
def do_register():

    if request.method == 'POST':
        username = request.form['username']
        password = sha256_crypt.hash(request.form['password'])

        mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        cursor = mydb.cursor()
        query = "INSERT INTO users(username,password) VALUES(%s,%s)"
        cursor.execute(query, (username, password))
        mydb.commit()
        cursor.close()

        return redirect(url_for('login_load'))


# The Login url loads the login page
# Login page allows user to input their username and password to login
# Other URL's redirect to this page if user is not logged in
@app.route('/login')
def login_load():
    if not session.get('logged_in'):
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("SELECT * from users")
        if cursor.rowcount != 0:
            return render_template('login.html')
        else:
            return redirect(url_for('register_load'))
    else:
        return redirect(url_for('dashboard_load'))


# Check users inputted username and password with user in the database
# If authenticated then redirect to dashboard page else display "Incorrect username/Password" message
@app.route('/login', methods=['POST'])
def do_login():

    if request.method == 'POST':
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("SELECT * from users")
        if cursor.rowcount != 0:
            myresult = cursor.fetchall()[0]
            if request.form['username'] == myresult[1] and sha256_crypt.verify(request.form['password'],myresult[2]):
                session['logged_in'] = True
                session['username'] = myresult[1]
                return redirect(url_for('dashboard_load'))
            else:
                return render_template('login.html', error="Incorrect Username or Password")
        else:
            return redirect(url_for('register_load'))


# Signs out user  and redirects to the login page
@app.route('/logout')
def do_admin_logout():
    if session.get('logged_in'):
        session['logged_in'] = False
        session['username'] = None
        return redirect(url_for('login_load'))
    else:
        return redirect(url_for('login_load'))


# The dashboard url loads the dashboard page
# The dashboard URL also handles POST methods from the dashboard for Stop(Config), Run(Config) and Dismiss(Notification)
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard_load():

    # Redirect to login if not signed in
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))

    else:

        if request.method == 'POST':

            # A "Stop" form action stops the current running configuration
            if request.form['action'] == "Stop":
                mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
                cursor = mydb.cursor(buffered=True)
                cursor.execute("SELECT * from configurations WHERE running = 1")
                if cursor.rowcount != 0:
                    runningconfig = cursor.fetchall()[0][0]
                    query = "UPDATE `configurations` SET `running` = '0' WHERE `id` = " + str(runningconfig)
                    cursor.execute(query)
                    mydb.commit()
                cursor.close()
                return redirect(url_for('dashboard_load'))

            # A "Run" form action runs the current selected configuration
            elif request.form['action'] == "Run":
                mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
                cursor = mydb.cursor(buffered=True)
                cursor.execute("SELECT * from configurations WHERE selected = 1")

                if cursor.rowcount != 0:
                    selectedconfig = cursor.fetchall()[0][0]
                    query = "UPDATE `configurations` SET `running` = '1', `startTime` = NOW() WHERE `id` = " + str(selectedconfig)
                    cursor.execute(query)
                    mydb.commit()
                cursor.close()
                #incubator.waiting(False)
                return redirect(url_for('dashboard_load'))

            # A "Dismiss" form action dismisses(sets database value of dismissed to 1) the notification selected
            elif request.form['action'] == "Dismiss":
                mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
                cursor = mydb.cursor(buffered=True)
                dismissednotification = request.form['id']
                query = "UPDATE `notifications` SET `dismissed` = '1' WHERE `id` = " + str(dismissednotification)
                cursor.execute(query)
                mydb.commit()
                cursor.close()
                return redirect(url_for('dashboard_load'))

        # Else the dashboard loads
        else:

            # Connect to database
            mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
            mycursor = mydb.cursor(buffered=True)

            # Get undismissed Notifications
            mycursor.execute("SELECT * FROM notifications WHERE dismissed = 0 ORDER BY timestamp DESC; ")
            notifications = mycursor.fetchall()

            # Get Selected Configuration
            mycursor.execute("SELECT * from configurations WHERE selected = 1")

            running = False
            starttime = ""

            # If a selected configuration exists
            if mycursor.rowcount != 0:
                selectedconfig = mycursor.fetchall()[0]

                # Check if the selected configuration is running
                if selectedconfig[8] == 1:
                    running = True
                    starttime = selectedconfig[9]

            # Else a selected configuration does not exist so a blank selectedconfig is created
            else:
                selectedconfig = ["", "", "", "", "", "", "", "", "", ""]

            return render_template('dashboard.html', notifications=notifications, selectedconfig=selectedconfig, running=running, rundate=starttime)


# The data url provides a json object of data from the database
@app.route('/data')
def data():
    # Connect to database
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
    mycursor = mydb.cursor()

    # Get values from database from the last 24 hours
    now = datetime.datetime.now()
    nowString = now.strftime("%Y-%m-%d %H:%M:%S")
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterdayString = yesterday.strftime("%Y-%m-%d %H:%M:%S")

    mycursor.execute("SELECT * FROM incubator WHERE timestamp BETWEEN '"+yesterdayString+"' AND '"+nowString+"' ORDER BY timestamp DESC; ")
    myresult = mycursor.fetchall()

    # Get undismissed Notifications
    mycursor.execute("SELECT * FROM notifications WHERE dismissed = 0 ORDER BY timestamp DESC; ")
    notifications = mycursor.fetchall()

    # Add data from database to temperature and humidity arrays
    temperatureData = []
    humidityData = []

    if not myresult:
        temperatureData.append(["0000-00-00 00:00:00", "0.0"])
        humidityData.append(["0000-00-00 00:00:00", "0.0"])

    else:
        for row in myresult:
            temperatureData.append([row[3].strftime("%Y-%m-%d %H:%M:%S"), str(row[1]).lstrip()])
            humidityData.append([row[3].strftime("%Y-%m-%d %H:%M:%S"), str(row[0]).lstrip()])

    return jsonify({'temperatureData': temperatureData, 'humidityData': humidityData})


# The configurations url loads the configurations page
# The configurations URL also handles POST methods from the dashboard for Stop(Config), Run(Config) and Dismiss(Notification)
@app.route('/configurations', methods=['GET', 'POST'])
def configuration_load():

    # Redirect to login if not signed in
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))

    else:

        if request.method == 'POST':

            # An "Add" form action adds a new configuration to the database
            if request.form['action'] == "Add":
                name = request.form['name']
                species = request.form['species']
                temperature = request.form['temperature']
                humidity = request.form['humidity']
                duration = request.form['duration']
                notes = request.form['notes']

                mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
                cursor = mydb.cursor()
                query = "INSERT INTO configurations(name,species,temperature,humidity,duration,notes) VALUES(%s,%s,%s,%s,%s,%s)"
                cursor.execute(query,(name,species,temperature,humidity,duration,notes))
                mydb.commit()
                cursor.close()
                return redirect(url_for('configuration_load'))

            # An "Edit" form action updates a configuration in the database
            elif request.form['action'] == "Edit":
                name = request.form['name']
                species = request.form['species']
                temperature = request.form['temperature']
                humidity = request.form['humidity']
                duration = request.form['duration']
                notes = request.form['notes']
                configid = request.form['configId']

                mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
                cursor = mydb.cursor()
                query = "UPDATE `configurations` SET `name` = '"+name+"'," \
                                                    " `species` = '"+species+"'," \
                                                    "`temperature` = "+temperature+"," \
                                                    " `humidity` = "+humidity+"," \
                                                    " `duration`= "+duration+"," \
                                                    " `notes`='"+notes+"' WHERE `id` = "+configid
                cursor.execute(query)
                mydb.commit()
                cursor.close()
                return redirect(url_for('configuration_load'))

            # A "Delete" form action deletes a configuration from the database
            elif request.form['action'] == "Delete":
                configid = request.form['configId']
                mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
                cursor = mydb.cursor()
                query = "DELETE FROM `configurations` WHERE `id` = " + configid
                cursor.execute(query)
                mydb.commit()
                cursor.close()
                return redirect(url_for('configuration_load'))

            # A "Select" form action sets a configuration in the database to selected
            elif request.form['action'] == "Select":
                configid = request.form['configId']
                mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
                cursor = mydb.cursor(buffered=True)
                cursor.execute("SELECT * from configurations WHERE selected = 1")
                if cursor.rowcount != 0:
                    selectedconfig = cursor.fetchall()[0][0]
                    query = "UPDATE `configurations` SET `selected` = '0',`running` = '0' WHERE `id` = " + str(selectedconfig)
                    cursor.execute(query)
                    mydb.commit()
                cursor.execute("UPDATE `configurations` SET `selected` = '1' WHERE `id` = " + configid)
                mydb.commit()
                query = "TRUNCATE `smartincubator`.`incubator`;"
                cursor.execute(query)
                mydb.commit()
                query = "TRUNCATE `smartincubator`.`notifications`;"
                cursor.execute(query)
                mydb.commit()
                cursor.close()
                return redirect(url_for('configuration_load'))

            # A "Stop" form action stops the current running configuration
            elif request.form['action'] == "Stop":
                mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
                cursor = mydb.cursor(buffered=True)
                cursor.execute("SELECT * from configurations WHERE running = 1")
                if cursor.rowcount != 0:
                    runningconfig = cursor.fetchall()[0][0]
                    query = "UPDATE `configurations` SET `running` = '0' WHERE `id` = " + str(runningconfig)
                    cursor.execute(query)
                    mydb.commit()
                cursor.close()
                return redirect(url_for('configuration_load'))

            # A "Run" form action runs the current selected configuration
            elif request.form['action'] == "Run":
                mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
                cursor = mydb.cursor(buffered=True)
                cursor.execute("SELECT * from configurations WHERE selected = 1")

                if cursor.rowcount != 0:
                    selectedconfig = cursor.fetchall()[0][0]
                    query = "UPDATE `configurations` SET `running` = '1' WHERE `id` = " + str(selectedconfig)
                    cursor.execute(query)
                    mydb.commit()
                cursor.close()
                return redirect(url_for('configuration_load'))

        # Else the configurations page loads
        else:
            mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
            cursor = mydb.cursor(buffered=True)

            # Get all the configurations
            cursor.execute("SELECT * from configurations")
            configs = cursor.fetchall()

            # Get the current selected configuration
            cursor.execute("SELECT * from configurations WHERE selected = 1")

            running = False
            starttime = ""

            # If a selected configuration exists
            if cursor.rowcount != 0:
                selectedconfig = cursor.fetchall()[0]

                # Check if the selected configuration is running
                if selectedconfig[8] == 1:
                    running = True
                    starttime = selectedconfig[9]

            # Else a selected configuration does not exist so a blank selectedconfig is created
            else:
                selectedconfig = ["", "", "", "", "", "", "", "", "", ""]

            # If there are n configurations create a blank array of configs
            if not configs:
                configs = []

            return render_template("configurations.html", configs=configs, selectedconfig=selectedconfig, running=running, rundate=starttime)

# The settings url loads the settings page
@app.route("/settings")
def settings_load():

    # Redirect to login if not signed in
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))

    else:
        # Connect to database
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        mycursor = mydb.cursor()

        # Select settings from the database
        mycursor.execute("SELECT * FROM settings")

        myresult = mycursor.fetchall();

        return render_template('settings.html')


# The help url loads the help page
@app.route("/help")
def help_load():

    # Redirect to login if not signed in
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))

    else:
        return render_template('help.html')


if __name__ == "__main__":
    app.secret_key = os.urandom(12)

    for process in psutil.process_iter():
        if process.cmdline() == ['python', 'incubator.py']:
            print("Found")
        else:
            print("Not Found")
            subprocess.Popen(["nohup", "python", "scripts/incubator.py"], env=os.environ, preexec_fn=os.setpgrp)
    app.run(debug=True, host='127.0.0.1', port=8080)
    #app.secret_key = 'capstone'
    #app.run(host='0.0.0.0', port=80)