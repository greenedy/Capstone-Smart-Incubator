
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import mysql.connector
import datetime
import os

app = Flask(__name__)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login_load'))
    else:
        return redirect(url_for('dashboard_load'))


@app.route('/login')
def login_load():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect(url_for('dashboard_load'))


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.method == 'POST':
        if request.form['password'] == 'password' and request.form['username'] == 'username':
            session['logged_in'] = True
            return redirect(url_for('dashboard_load'))
        else:
            flash('wrong password!')


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
        timeString = now.strftime("%Y-%m-%d %H:%M")

        mycursor.execute("SELECT * FROM incubator ORDER BY id DESC LIMIT 1")

        myresult = mycursor.fetchall();

        if not myresult:
            humidity = 0
            temperature = 0

        else:
            for row in myresult:
                humidity = row[0]
                temperature = row[1]

        templateData = {
            'humidity': humidity,
            'temperature': temperature,
            'time': timeString
        }
        return render_template('dashboard.html', **templateData)


# @app.route("/configurations")
# def configurations_load():
#     if not session.get('logged_in'):
#         return redirect(url_for('login_load'))
#
#     else:
#         # Connect to database
#         mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
#         mycursor = mydb.cursor()
#
#         now = datetime.datetime.now()
#         timeString = now.strftime("%Y-%m-%d %H:%M")
#
#         mycursor.execute("SELECT * FROM configurations")
#         myresult = mycursor.fetchall();
#       #  for row in myresult:
#
#         templateData = {
#         }
#         return render_template('configurations.html', **templateData)

@app.route('/configurations', methods=['GET', 'POST'])
def get_data():
    if request.method == 'POST':
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
        return render_template("configurations.html")
    else:
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
        cursor = mydb.cursor()
        cursor.execute("SELECT * from Configurations")
        configs = cursor.fetchall()
        cursor.execute("SELECT * from Configurations where running = 1")
        runningconfig = cursor.fetchall()

        if not runningconfig:
            humidity = 0
            temperature = 0

        else:
            humdity=0
        return render_template("configurations.html", configs=configs, runningConfig=runningconfig)

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