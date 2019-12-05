# Smart-Incubator
SEG4910/SEG4911 Capstone Project Smart Incubator

Welcome to the Pincubator(smart incubator) read me file.

To use the online incubator website you must have the same build of incubator for te softeare to be compatiable. You may change the incubator.py script to utilize your specific hardware if you so choose.

Our build is here: https://github.com/greenedy/Capstone-Smart-Incubator/wiki/Incubator-Build 


First create an account on Dataplicity and follow the instructions on how to link your rasberry pi to your account

https://www.dataplicity.com/


Then to use your gmail account to send email:

If you dont have 2 factor authentication follow these instructions to use your credentials: 
https://support.google.com/accounts/answer/6010255

If you have 2-factor authentication on your account use these instructions to generate an app Password:
https://support.google.com/accounts/answer/185833


Then use your credentials to update the app.py and incubator.py scripts where it says: 

gmail_user = 'email@gmail.com'
gmail_pwd = 'password'

Create a MySQL database on your pi following these instructions:
- https://pimylifeup.com/raspberry-pi-mysql/
- run the SmartIncubatorDatabase.sql script to create the database
- run the initialData.sql to load the initial data into the database

Then upload all the code on to the rasberry pi and start the app.py script and incubator.py script.

Then using your dataplicity url visit https://YOURURLHERE.dataplicity.io/login

This will send you to the registration page where you can input your email and a username and password to access the incubator website

Once registered you can login with your credentials

For more information on the app visit the wiki: https://github.com/greenedy/Capstone-Smart-Incubator/wiki
