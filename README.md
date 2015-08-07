# servicemap
ServiceMap is a tool to correlate and graph TCP/UDP connections between servers.

This is a work in progress. 
BYU web template is included, feel free to switch it out for your own branding and just edit out those portions of the HTML files.

Installation instructions:

Collector:
install Python, Apache, MySQL/MariaDB, rsyslog, NetworkX, Python MySQL connector, other Python packages I can't remember (keep installing until cgi scripts stop complaining.
use rsyslog's DB create script to set up database
run LogSummary.sql create script
change DB connect password in cgi scripts and iptables-collector.conf
start rsyslog listening on UDP and configure to write messages to DB (udpListen.conf, iptables-collector.conf)
edit cgi-bin/hostList.py for list of desired subnets to be shown/graphed
enable Apache or other web server CGI and put cgi-bin and html directories in place
link connectionSummary.py to cron to be run at desired frequency (10 minutes seems to work well)


Nodes:
add iptablesRules.txt lines to iptables configuration file
add iptables.conf rsyslog rule and change hostname to point at collector
