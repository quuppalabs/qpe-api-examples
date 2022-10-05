# This is a first version of a log parser that sends the data to Influx
# At the moment it covers certain types of lines for tagStatusLog but may be extended to support other line
# and logfile types by some regex magic


import re
import os
import sys
import json
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

# Setting the InfluxDB bucket, user, token and url
with open("keys/keys.json") as json_file:
    keys = json.load(json_file)
    influx_creds = keys["influx_db_system_monitor"]

##keys.json looks like:
# {
#     "influx_db_system_monitor": {
#         "token": "your token",
#         "org": "your org",
#         "url": "https://eu-central-1-1.aws.cloud2.influxdata.com",
#         "bucket": "NameOfYourBucket"
#     }
# }

# Initializing the InfluxDBClient and api
client = InfluxDBClient(url=influx_creds["url"], token=influx_creds["token"], org=influx_creds["org"], verify_ssl=False)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Initialize list where all different metrics are stored
metrics = []

# Setting up the tagStatusLog parser
# Set keywords/strings that the line has to contain in order to be read
lineKeywords = ["Storage->","Receive","Current"]

# Set keywords for fields in the line that are sent to Influx
fieldKeywords = ["Storage->Triggered","Default->Triggered","Triggered->Triggered","*->Temporary","Receive req counter","Failed decrypt container","New commands","Commands","Success","Unique DF","Current consumption: alarm","voltage","df counter","data counter","conf counter"]

# Set keywords for splitting fields from certain word
splitKeywords = ["alarm"]

# Local path of the directory where the files are (this script only handles one folder at a time)
# Gotten from startup params for the program - if not given throw error
if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    sys.exit("You need to provide a path for the folder you want to process as a startup parameter (ie. python TLMParser.py C:\\opt\quuppa\\tagStatusLogs\\20220916\\)")

# Creates a list of files within the given directory
files = os.listdir(path)

# Reads through all the files listed
for file in files:
    with open(path + file, "r") as data:
        for line in data:
            # Check if line contains any of the keywords
            for lineKeyword in lineKeywords:
                if lineKeyword in line:
                    # If keyword found, initialize measurement for Influx
                    metric = {}
                    tags = {}
                    fields = {}
                    # Setting tag id as searchable key for measurement
                    tags["tagId"] = file.split("_")[1]
                    fields["tagId"] = file.split("_")[1]
                    # Split the line to list from comma to get a list of fields (to be converted to key value pairs later)
                    itemlist = line.split(",")
                    # Setting first field (unix timestamp) as the timestamp for measurement
                    metric["time"] = datetime.utcfromtimestamp(int(itemlist[0]) / 1000).isoformat()

                    # Iterating through the list of fields to parse them
                    for item in itemlist:
                        # Parsing individual field with rule 'space followed by a number'
                        parsedItem = re.split(r'\s+(?=\d)|(?<=\d)\s+', item)
                        # Splitting based on split keywords. Split happens after the keyword.
                        for splitKeyword in splitKeywords:
                            if any(splitKeyword in string for string in parsedItem):
                                parsedItem = parsedItem[0].split(splitKeyword)
                                parsedItem[0] += splitKeyword
                        # Removing blanks from parse results
                        parsedItem = list(filter(None, parsedItem))
                        # Iterating through field keywords
                        for fieldKeyword in fieldKeywords:
                            # Checking if field keyword exists in any part of the field string (because of possible blanks in string)
                            if any(fieldKeyword in string for string in parsedItem):
                                # If the field array is longer than 1 (likely to be a key value pair)
                                if len(parsedItem) > 1:
                                    # Check if it's string or int and convert accordingly and add to Influx fields list with value
                                    if parsedItem[1].isdigit():
                                        fields[parsedItem[0].lstrip(" ")] = int(parsedItem[1].lstrip(" "))
                                    elif parsedItem[1] == "false":
                                        fields[parsedItem[0].lstrip(" ")] = 0
                                    elif parsedItem[1] == "true":
                                        fields[parsedItem[0].lstrip(" ")] = 1
                                    else:
                                        fields[parsedItem[0].lstrip(" ")] = parsedItem[1].lstrip(" ")
                                # If the field array contains only one entry, we'll parse that entry and take the last word as value
                                # This is a hack especially for current consumption alarm
                                else:
                                    # Checking if value is int, boolean or string and adding to Influx field list
                                    print("something else")
                                    # if parsedItem[0].isdigit():
                                    #     fields[parsedItem[0][0:-5]] = int(parsedItem[0].split(" ")[-1])
                                    # elif parsedItem[0].split(" ")[-1] == "false":
                                    #     fields[parsedItem[0][0:-5]] = 0
                                    # elif parsedItem[0].split(" ")[-1] == "true":
                                    #     fields[parsedItem[0][0:-5]] = 1
                                    # else:
                                    #     fields[parsedItem[0][0:-5]] = parsedItem[0].split(" ")[-1]
                    metric['measurement'] = "tagStatusLog"
                    metric['tags'] = tags
                    metric['fields'] = fields
                    metrics.append(metric)

# Write the created metrics object to the bucket you want
print("Writing data to influx cloud...")


try:
    write_api.write(bucket=influx_creds["bucket"],org=influx_creds["org"],record=metrics)
    print("Writing data to influx cloud: Completed")
except Exception as err:
    print(err)
    print("Could not post to Influx Cloud!!!!")


