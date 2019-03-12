
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import mysql.connector
import datetime
import os
import html

app = Flask(__name__)

#if url is emoty then it redirects to the login
@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))
    else:
        return redirect(url_for('dashboard_load'))

#The register url loads the register html page
#Add variable for user and pass for pi switch
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


@app.route('/register', methods=['POST'])
def do_register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        cursor = mydb.cursor()
        query = "INSERT INTO users(username,password) VALUES(%s,%s)"
        cursor.execute(query, (username, password))
        mydb.commit()
        cursor.close()
        return redirect(url_for('login_load'))

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


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.method == 'POST':

        mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        cursor = mydb.cursor(buffered=True)
        cursor.execute("SELECT * from users")
        if cursor.rowcount != 0:
            myresult = cursor.fetchall()[0];
            if request.form['password'] == myresult[1] and request.form['username'] == myresult[2]:
                session['logged_in'] = True
                return redirect(url_for('dashboard_load'))
            else:
                flash('wrong password!')
        else:
            return redirect(url_for('register_load'))


@app.route('/logout')
def do_admin_logout():
    if session.get('logged_in'):
        session['logged_in'] = False
        return redirect(url_for('login_load'))
    else:
        return redirect(url_for('login_load'))


@app.route("/dashboard")
def dashboard_load():
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))

    else:
        # Connect to database
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        mycursor = mydb.cursor()

        now = datetime.datetime.now()
        nowString = now.strftime("%Y-%m-%d %H:%M:%S")
        yesterday = datetime.datetime.now().replace(day=now.day - 1)
        yesterdayString = yesterday.strftime("%Y-%m-%d %H:%M:%S")

        mycursor.execute("SELECT * FROM incubator WHERE timestamp BETWEEN '"+yesterdayString+"' AND '"+nowString+"' ORDER BY timestamp DESC; ")

        myresult = mycursor.fetchall()

        mycursor.execute("SELECT * FROM notifications WHERE timestamp BETWEEN '"+yesterdayString+"' AND '"+nowString+"' ORDER BY timestamp DESC; ")

        notifications = mycursor.fetchall()

        temperatureData = []
        humidityData = []

        if not myresult:
            temperatureData.append(["0000-00-00 00:00:00", "0.0"])
            humidityData.append(["0000-00-00 00:00:00", "0.0"])

        else:
            for row in myresult:
                temperatureData.append([row[3].strftime("%Y-%m-%d %H:%M:%S"),str(row[1]).lstrip() ])
                humidityData.append([row[3].strftime("%Y-%m-%d %H:%M:%S"),str(row[0]).lstrip() ])

        templateData = {
            'temperatureData': temperatureData,
            'humidityData': humidityData
        }
        return render_template('dashboard.html', **templateData, notifications=notifications)


#

@app.route('/configurations', methods=['GET', 'POST'])
def get_data():
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))

    else:
        if request.method == 'POST':
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
                return redirect(url_for('get_data'))
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
                return redirect(url_for('get_data'))
            elif request.form['action'] == "Delete":
                configid = request.form['configId']
                mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
                cursor = mydb.cursor()
                query = "DELETE FROM `configurations` WHERE `id` = " + configid
                cursor.execute(query)
                mydb.commit()
                cursor.close()
                return redirect(url_for('get_data'))
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
                cursor.close()
                return redirect(url_for('get_data'))
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
                return redirect(url_for('get_data'))
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
                return redirect(url_for('get_data'))
        else:
            mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
            cursor = mydb.cursor(buffered=True)
            cursor.execute("SELECT * from configurations")
            configs = cursor.fetchall()
            cursor.execute("SELECT * from configurations WHERE selected = 1")
            if cursor.rowcount != 0:
                selectedconfig = cursor.fetchall()[0]

            else:
                selectedconfig = ["","","","","","","","","",""]

            if not configs:
                 configs =[]

            return render_template("configurations.html", configs=configs, selectedconfig=selectedconfig)

@app.route("/settings")
def settings_load():
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))

    else:
        # Connect to database
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        mycursor = mydb.cursor()

        now = datetime.datetime.now()
        timeString = now.strftime("%Y-%m-%d %H:%M")

        #mycursor.execute("SELECT * FROM settings")

        # myresult = mycursor.fetchall();

        # for row in myresult:


        templateData = {

        }
        return render_template('settings.html', **templateData)


@app.route("/help")
def help_load():
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))

    else:
        return render_template('help.html')


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='127.0.0.1', port=8080)
    #app.secret_key = 'capstone'
    #app.run(host='0.0.0.0', port=80)