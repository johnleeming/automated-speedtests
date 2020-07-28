#!/usr/bin/python3.5
import os
import csv
import datetime
import time
import json



print("""
-----------------------------
Starting automated-speedtests
-----------------------------
""")



ping = False
down = False
up = False
img = False
tests = 0



with open('/home/pi/automated-speedtests/config.json', 'r') as f:
    config = json.load(f)

def pingTest():
    hostname = config['hostname']
    response = os.system("ping -c 1 " + hostname)
    if response == 0:
        pingResult = True
    else:
        pingResult = False

    return pingResult


def speedTest(ping, down, up, img, tests):
    print("\nConducting speed test...")
    speedTestOutput = os.popen("python " + config['speedtestPath'] + " --simple --share").read()
    print("Speed test complete")

    lines = speedTestOutput.split("\n")
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

    print("\n------------------------------------------------------")
    print(date + "\n" + speedTestOutput + "------------------------------------------------------\n")
    #Set speeds to 0 if speedtest-cli couldn't connect
    if "Cannot" in speedTestOutput:
        ping = 100
        down = 0
        up = 0
        img = "noimg"

    #Extract values for ping, download and upload
    else:
        ping = lines[0].split(' ')[1]
        down = lines[1].split(' ')[1]
        up = lines[2].split(' ')[1]
        img = lines[3].split(' ')[2]


    #Save the data to file for local network plotting
    fileSpeedResults = open(config['webserverPath'] + "/speedresults.csv", 'a')
    writer = csv.writer(fileSpeedResults)
    writer.writerow((date, ping, down, up))
    fileSpeedResults.close()

    #save just latest value for status display
    with open('/home/pi/automated-speedtests/latest.csv', 'w') as latest:
        latest.write(date + ',' + ping + ',' + down + ',' + up)

    ping = float(ping)
    down = float(down)
    up = float(up)

    tests += 1

    return(ping, down, up, img, tests)



downtime = 0
start_time = time.time()
pingResult = pingTest()

while pingResult == False:
    downtime = time.time() - start_time
    print("No network connection detected")
    pingResult = pingTest()

if pingResult == True:
    if downtime > 0:
        print("Network connection re-established. Downtime: ", downtime)
    else:
        print("Network connection detected")
        ping, down, up, img, tests = speedTest(ping, down, up, img, tests)

               
