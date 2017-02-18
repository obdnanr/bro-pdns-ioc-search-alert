# Written by Brandon Kelley Jan 13th 2017
# Email alerting for PDNS IOC searching
# Version 1.0.0
import smtplib
import csv
import os
import re
from datetime import *

# Prepare for date comparison
today = date.today()
today = datetime.combine(today, datetime.min.time())

# Setup email alerting
sender = 'server@company.com'
receivers = ['user@company.com']

# Compile date regex and already emailed regex
patn = re.compile('20\d{2}-\d{2}-\d{2}')

# File that will be watched for @ symbol, so it knows it already sent an email
watchfile = open('watchfile.csv', 'r+w')
finalhit = open('finalIOChit.csv', 'r')

# Open finalIOChit.csv, check the watchfile for @'s, send alert if @ isn't present
# and send alert only if the last hit is == today. 
for hit in finalhit:
    for match in patn.findall(hit):
        val = datetime.strptime(match, '%Y-%m-%d')
        if val == today:
            watchfile.write(hit)
            if hit != watchfile.read():
                message = """From:server <server@company.com>
To: User <user@company.com>
Subject: Passive DNS hit 
"""
                subject = ' ' + str(hit)
                messagefull = message + subject
                try:
                    smtpObj = smtplib.SMTP('emailserver')
                    smtpObj.sendmail(sender, receivers, messagefull)
                except SMTPException:
                    print "Error: unable to send email"