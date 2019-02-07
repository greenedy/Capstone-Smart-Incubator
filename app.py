
from flask import Flask, flash, redirect, render_template, request, session, abort
import mysql.connector
import datetime
import os

app = Flask(__name__)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')

    else:
        return "Welcome to Pincubator!"


@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'username':
        session['logged_in'] = True

    else:
        flash('wrong password!')
    return home()


@app.route("/dashboard")
def dashboardLoad():
    # Connect to database
    mydb = mysql.connector.connect(host="localhost", user="root", passwd="password", database="smartincubator")
    mycursor = mydb.cursor()

    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")

    mycursor.execute("SELECT * FROM incubator ORDER BY id DESC LIMIT 1")

    myresult = mycursor.fetchall();

    for row in myresult:
        humidity = row[0]
        temperature = row[1]

    templateData = {
        'humidity': humidity,
        'temperature': temperature,
        'time': timeString
    }
    return render_template('dashboard.html', **templateData)

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
app.run(debug=True, host='127.0.0.1', port=8080)