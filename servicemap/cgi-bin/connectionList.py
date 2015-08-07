#!/usr/bin/env python

# log into mysql database, get list of hosts, write to JSON.

from __future__ import print_function
from decimal import Decimal
from datetime import datetime, date, timedelta
import mysql.connector
import networkx as nx
from networkx.readwrite import json_graph
import json
import sys
import collections
import cgi
import cgitb; cgitb.enable()
from socket import gethostbyaddr

def nslooky(ip):
    try:
        output = gethostbyaddr(ip)
        return output[0]
    except:
        output = ip
        return output

def main():
    
    # PROPERTIES
    debug = False
    form = cgi.FieldStorage()
    
    # Connect with the MySQL Server
    cnx = mysql.connector.connect(user='rsyslog', database='Syslog', password='changeme')
    
    # Get buffered pcursor
    curA = cnx.cursor(buffered=True)
    
    r = form.getlist('hostList')
    sqlSeparatorDst = "' OR dstip='"
    dstFilter = sqlSeparatorDst.join(r)

    sqlSeparatorSrc = "' OR srcip='"
    srcFilter = sqlSeparatorSrc.join(r)

    r2 = form.getlist('portList')
    sqlSeparatorPort = "' OR dstport='"
    portFilter = sqlSeparatorPort.join(r2)

    get_data = ("select srcip, dstip, proto, dstport, counter, lastseen, firstseen from LogSummary where ((dstip='" + dstFilter + "' OR srcip='" + srcFilter + "') AND (dstport='" + portFilter + "')) AND counter > 50 order by INET_ATON(dstip)")
    #print("Content-Type: text/html")
    #print("")
    #print(get_data)        


    # get the data
    curA.execute(get_data)
    cnx.commit()
    cnx.close()
    
    results = []
    G = nx.DiGraph()

    # iterate through results and build dictionary with hostname:ip
    for (srcip, dstip, proto, dstport, counter, lastseen, firstseen) in curA:
        dict = {}
        dict["srcip"] = nslooky(srcip)
        dict["dstip"] = nslooky(dstip)
        dict["proto"] = proto
        dict["dstport"] = dstport
        dict["counter"] = counter
        dict["lastseen"] = str(lastseen)
        dict["firstseen"] = str(firstseen)
        results.append(dict)

        # now add node to graph
        G.add_node(srcip)
        G.node[srcip]['hostname'] = dict["srcip"]
        G.add_node(dstip)
        G.node[dstip]['hostname'] = dict["dstip"]
        G.add_edge(srcip, dstip)
        G.edge[srcip][dstip]['dstport'] = dstport
        G.edge[srcip][dstip]['counter'] = counter
        G.edge[srcip][dstip]['proto'] = proto



    print("Content-Type: application/json")
    #print("Content-Type: text/html")
    print("")
    #print(get_data)
    #print("<p>")
    #print(json.dumps(results))
    #print(json.dumps(json_graph.node_link_data(G)))
    resultJson = json.loads(json.dumps(results))
    graphJson = json.loads(json.dumps(json_graph.node_link_data(G)))
    response = {"list": resultJson, "graph": graphJson}
    print(json.dumps(response))
    
if __name__ == "__main__":
    main()
