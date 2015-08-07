#!/usr/bin/env python

# log into mysql database, read from rsyslog's SystemEvents table, 
# summarize data into another table, then delete the rows we summarized from SystemEvents.

from __future__ import print_function
from decimal import Decimal
from datetime import datetime, date, timedelta
import mysql.connector
import networkx as nx
from networkx.readwrite import json_graph
from socket import gethostbyaddr
from socket import gethostbyname
import json
import sys


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
    count = 0
    debug = False
    target = getip(argv[0])
    
    # Connect with the MySQL Server
    cnx = mysql.connector.connect(user='rsyslog', database='Syslog', password='changeme')
    
    # Get two buffered pcursors
    curA = cnx.cursor(buffered=True)
    
    #get_data =  ("SELECT * FROM LogSummary")
    get_data =  ("SELECT * FROM LogSummary where srcip like '" + target + "' or dstip like '" + target + "' and proto='TCP' and count>20")
        
        
    # get the data
    curA.execute(get_data)
    cnx.commit()
    cnx.close()
    
    G = nx.DiGraph()
    
    #print("curA count is: ", curA.count())
    # iterate through results and build graph
    for (id, srcip, dstip, proto, srcport, dstport, count, lastseen, firstseen) in curA:
        # networkx silently ignores existing nodes when adding.
        G.add_node(srcip)
        # print("srcip is ", nslooky(srcip))
        G.node[srcip]['hostname'] = nslooky(srcip)
        G.add_node(dstip)
        G.node[dstip]['hostname'] = nslooky(dstip)
        G.add_edge(srcip, dstip)
        G.edge[srcip][dstip]['dstport'] = dstport
        G.edge[srcip][dstip]['count'] = count    
        G.edge[srcip][dstip]['proto'] = proto
    
    
    # write out JSON data
    data = json_graph.node_link_data(G)
    with open('/byu/adm.clawsonj/code/flask/app/static/graph.json', 'w') as outfile:
        json.dump(data, outfile)
    #print(json.dumps(data))
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Incorrect number of arguments.")
        print("Usage: graphGen.py [hostname]")
    else:
        main(sys.argv[1:])
