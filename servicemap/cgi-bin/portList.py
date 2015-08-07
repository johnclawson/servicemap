#!/usr/bin/env python

# log into mysql database, get list of hosts, write to JSON.

from __future__ import print_function
from decimal import Decimal
from datetime import datetime, date, timedelta
import mysql.connector
import json
import sys
import collections
import cgi
import cgitb; cgitb.enable()

def main():
    
    # PROPERTIES
    debug = False
    form = cgi.FieldStorage()
    
    # Connect with the MySQL Server
    cnx = mysql.connector.connect(user='rsyslog', database='Syslog', password='changeme')
    
    # Get buffered pcursor
    curA = cnx.cursor(buffered=True)
    
    r = form.getlist('hostList')
    sqlSeparator = "' or dstip='"
    dstFilter = sqlSeparator.join(r)

    srcSeparator = "'or srcip='"
    srcFilter = srcSeparator.join(r)

    fields = "<p>"+ str(r) +"</p>"        

    #get_data = ("select distinct(dstport) from LogSummary where dstip='" + dstFilter + "' and counter > 50 order by dstport")
    get_data = ("select distinct(dstport) from LogSummary where (dstip='" + dstFilter + "' or srcip='" + srcFilter + "')  and counter > 50 order by dstport")
        
    # get the data
    curA.execute(get_data)
    cnx.commit()
    cnx.close()
    
    results = []
    # iterate through results and build dictionary with hostname:ip
    for (dstport) in curA:
        port = dstport[0]
        results.append(port)

    print("Content-Type: application/json")
    #print("Content-Type: text/html")
    print("")
    #print(get_data)
    #print("<p>")
    print(json.dumps(results))
    
if __name__ == "__main__":
    main()
