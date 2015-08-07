#!/usr/bin/env python

# log into mysql database, get list of hosts, write to JSON.

from __future__ import print_function
from decimal import Decimal
from datetime import datetime, date, timedelta
import mysql.connector
from socket import gethostbyaddr
from socket import gethostbyname
import json
import sys
import collections


def nslooky(ip):
    try: 
        output = gethostbyaddr(ip)
        return output[0]
    except: 
        output = ip 
        return output

def getip(hostname):
    try:
        output = gethostbyname(hostname)
        return output
    except:
        return "hostname not found."

def main(argv):
    
    # PROPERTIES
    debug = False
    
    # Connect with the MySQL Server
    cnx = mysql.connector.connect(user='rsyslog', database='Syslog', password='changeme')
    
    # Get buffered pcursor
    curA = cnx.cursor(buffered=True)
    
    # build list of desired subnets, in sql syntax
    # addresses not in this list will be filtered out of tool
    subnets = [
            '10.1.8.%', # Windows
            '10.1.9.%', # Linux
            ]
    
    sqlSeparator = "' or dstip like '"
    subnetFilter = sqlSeparator.join(subnets)

    get_data = ("select distinct(dstip) from LogSummary where (dstip like '" + subnetFilter + "') and counter > 50 order by INET_ATON(dstip)")
        
    # get the data
    curA.execute(get_data)
    cnx.commit()
    cnx.close()
    
    results = {}
    # iterate through results and build dictionary with hostname:ip
    for (dstip) in curA:
        addr = dstip[0]
        results[nslooky(addr)] = addr

    sortedResults = collections.OrderedDict(sorted(results.items()))
    print("Content-Type: application/json")
    print("")
    print(json.dumps(sortedResults))
    
if __name__ == "__main__":
    main(sys.argv[1:])
