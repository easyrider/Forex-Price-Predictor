import smtplib
import json

def sendEmail(sender, target, msg):
	server = smtplib.SMTP('smtp.gmail.com',587)
	server.ehlo()
	server.starttls()
	with open('config.json', 'r') as f:
		config = json.load(f)
	server.login(config['emailUser'], config['emailPass'])	
	server.sendmail(sender, target, msg)
	server.quit()



