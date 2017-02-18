#!/usr/bin/python
# Written by Brandon Kelley Jan 10th 2017
# Query a list of domain addresses to the PDNS database via API URL query.
# The Domain IOC list is hosted of CRITS, but feel free to use any webserver.
# Version 1.0.0
import os
import requests
import json
import re
import subprocess
import csv
from datetime import *

IOC_URL = 'http://critsserver/domain.txt'

# Cleanup files
try:
    os.remove('domain.txt')
except OSError:
    print("Can't remove domain.txt")
try:
    os.remove('domain_ioc_hits.json')
except OSError:
    print("Can't remove domain_ioc_hits.json")
try:
    os.remove('domain_ioc_hits2.csv')
except OSError:
    print("Can't remove domain_ioc_hits2.csv")
try:
    os.remove('watchfile.csv')
except OSError:
    print("Can't remove watchfile.csv")

# Pull file down from CRITS webserver.
IOC_URL = subprocess.call(['/usr/bin/wget', IOC_URL])

# Perform http request for each domain in IOC_URL against PDNS API URL.
with open('domain.txt','r+') as inputfile:
    for row in inputfile:
        # Remove new line from requested URL (shows up as 0%A if you don't do this).
        row = re.sub('\n','',row)
        url = "http://PDNSserver:8081/dns/"
        result = requests.get(url+row)
        for item in result:
            # Discard results with the standard 15 characters in all hits (false hits)
            if len(result.text) > 15:
                with open('domain_ioc_hits.json','a') as hits:
                    json.dump(result.text, hits)
                    hits.write('\n\n')

# This file contains your hits in a readable format.
copiedfile = open('domain_ioc_hits2.csv','w')

# Formatting IOC hits into readable format and outputing to file above ^.
with open('domain_ioc_hits.json','r+a') as pretty:
    for record in pretty:
        record = re.sub(',',',\n',record)
        record = re.sub(r"\\",'',record)
        record = re.sub('[|{|}|]|"','',record)
        copiedfile.write(record)

copiedfile.close()
anotherfile = open('anotherfile.csv','w+a')

# Alerting for hits on domain_ioc_hits2.csv
with open('domain_ioc_hits2.csv', 'r') as csvfile:
    for record in csvfile:
        secondrecord = record
        query = re.search(r'query: *.*.*,',record)
        lastseen = re.findall(r'last: 20\d{2}-\d{2}-\d{2} ',secondrecord)
        anotherfile.write(' '.join(lastseen))
        if query:
            anotherfile.write(query.group(0))
            anotherfile.write('\n')

# Closing files
anotherfile.close()
copiedfile.close()
# Call shell script to sort | uniq and out to a file called finalIOChit.csv
subprocess.call(['/bin/sh', 'sortuniq.sh'])
