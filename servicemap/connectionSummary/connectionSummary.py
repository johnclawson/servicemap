#!/usr/bin/env python

# log into mysql database, read from rsyslog's SystemEvents table, 
# summarize data into another table, then delete the rows we summarized from SystemEvents.

from __future__ import print_function
from decimal import Decimal
from datetime import datetime, date, timedelta
import mysql.connector

# PROPERTIES
counter = 0
debug = False

print(str(datetime.now()), " STARTING")

# Connect with the MySQL Server
cnx = mysql.connector.connect(user='rsyslog', database='Syslog', password='changeme')

# Get two buffered pcursors
curA = cnx.cursor(buffered=True)
curB = cnx.cursor(buffered=True)
curC = cnx.cursor(buffered=True)

# Query to get the data we care about sent by iptables logging to syslog   
get_data = (
    "SELECT ID, FromHost, DeviceReportedTime, Message FROM SystemEvents "
    "where Message like '%newConn%' AND Message not like '%127.0.0.1%' order by DeviceReportedTime limit 500000")
    
delete_data = ("delete from SystemEvents where ID = \'%s\'")
delete_all_data = ("delete from SystemEvents")
    
# get the data
curA.execute(get_data)

# clean up SystemEvents table
try:
    print("Cleaning up fetched logs.")
    curC.execute(delete_all_data)
except mysql.connector.Error as err:
    print("Had a problem with the database: {}".format(err))

# UPDATE and INSERT statements for the LogSummary table
insert_log_summary = (
    "INSERT INTO LogSummary (srcip, dstip, proto, srcport, dstport, counter, lastseen, firstseen) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE counter=counter+1, lastseen=VALUES(lastseen)")

# iterate through results and do string parsing on the text message
reversed = 0
reversed2049 = 0

for (ID, FromHost, DeviceReportedTime, Message) in curA:
    messageList = Message.split(" ")
    messageDict = {}    
    
    # build dictionary from valid parts of iptables message
    for index, item in enumerate(messageList):
        if "=" in item:
            parts = item.split("=")
            if parts[1]:
                messageDict[parts[0]] = parts[1]
  
    try:
        if 'DPT' in messageDict:
            # convert strings to ints so we can compare them
            messageDict['DPT'] = int(messageDict['DPT'])
            messageDict['SPT'] = int(messageDict['SPT'])

            if messageDict['DPT'] <= messageDict['SPT'] and messageDict['SPT'] != 2049:
                if debug and messageDict['SPT'] == 2049:
                    print("normal destination ", messageDict['DPT'], "; source ", messageDict['SPT'])
                sourcePort = messageDict['SPT']
                destinationPort = messageDict['DPT']
                sourceHost = messageDict['SRC']
                destinationHost = messageDict['DST']
            
            elif messageDict['DPT'] != 2049:
                sourcePort = messageDict['DPT']
                destinationPort = messageDict['SPT']
                sourceHost = messageDict['DST']
                destinationHost = messageDict['SRC']
                reversed += 1
                if debug:
                    print("reversed destination ", messageDict['DPT'], " to source and source ", messageDict['SPT'] ," to destination.")
            else:
                sourcePort = messageDict['SPT']
                destinationPort = messageDict['DPT']
                sourceHost = messageDict['SRC']
                destinationHost = messageDict['DST']


            curB.execute(insert_log_summary,
                (sourceHost, destinationHost, messageDict['PROTO'], sourcePort, destinationPort, "1", DeviceReportedTime, DeviceReportedTime))

        #curC.execute(delete_data, (ID))
        counter += 1

    except mysql.connector.Error as err:
        print("Had a problem with the database: {}".format(err))
    

print("Processed records:", counter)
if debug:
    print("Reversed source/destination:", reversed)
    print("Reversed 2049 source/destination:", reversed2049)
    
print(str(datetime.now()), " FINISHED")
print("----------")
print("")

cnx.commit()
cnx.close()
exit()

