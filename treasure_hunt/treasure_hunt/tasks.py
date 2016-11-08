# how to run celery server
# celery -A treasure_hunt(app_name in _celery.py) worker -l info  (-l -> loglevel)

from __future__ import absolute_import

import smtplib

from treasure_hunt._celery import app


@app.task
def send_email(url, username, email,purpose):	
	ACTIVATION = 'ACTIVATION'
	CHANGE_PASSWORD = 'CHANGE_PASSWORD'

	fromaddr = 'ENTER YOUR EMAIL HERE'
	password = 'ENTER YOUR PASSWORD HERE'
	my_username = fromaddr

	if purpose == ACTIVATION:
		msg = "\r\n".join([
				  "From: NJATH" ,
				  "To: " + email  ,
				  "Subject: Activate your NJATH Account",
				  "",
				  "Thanks for registering for NJATH- Not Just Another Treasure Hunt",
				  "Your username is : " + username,
				  "\n", 
				  "Forgot your username - No Problem.\n You can always use your email address to login. Remember!!", 
				  "\n",
				  "Click on this link to activate your account " + url,
				  "\n\n",
				  "With Best Regards,",
				  "Prince",
				  "Junior Year, IIT Patna",
				  "contact : 9006697127",
			 	])

	elif purpose == CHANGE_PASSWORD:
		msg = "\r\n".join([
				  "From: " + fromaddr,
				  "To: " + email  ,
				  "Subject: Request for changing NJATH Account Password",
				  "",
				  "Request is received for password change for your account",
				  "Your username is : " + username,
				  "\n",
				  "Click on this link to change your password " + url,
				  "\n", 
				  "If this was not you, please ignore this mail",
				  "\n\n",
				  "With Best Regards,",
				  "Prince",
				  "Junior Year, IIT Patna",
				  "contact : 9006697127",
		 	])

	server = smtplib.SMTP_SSL()
	server.connect("smtp.gmail.com",465)
	server.ehlo()
	# server.starttls()
	server.login(my_username,password)
	server.sendmail(fromaddr, email, msg)
	server.quit()
