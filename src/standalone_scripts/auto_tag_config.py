#!/usr/bin/env python3.9
# Python 3.9.7
"""
The process here is written to be understood, not to be as 'pythonic' as possible.

This script handles only the most basic parts of automatically configured tags.
There are many ways this could be extended including, but not limited to:
- Handling tags that do not support configuration
- Persisting the data of configured tags with the import/export tag commands
- Handling tags that have a low battery 
- Handling tags repeatedly fail to configure

The general process is as follows:
- Get all tags
- Filter for tags that are unknown and not already in process
- Start configuring them
- Retry configuration if a status warranting that is returned
- If configuration is successful, add the tags to a group that denotes that
- Sleep and Repeat

"""


__author__ = "Quuppa"


from pprint import pprint
import time
import urllib.parse as urlparse

import requests


################# url strings #################
QPE_SERVER = "http://localhost:8080"
# for this script, the getTagData format will not change. Query parameters can be hardcoded
tag_data_url = urlparse.urljoin(
    QPE_SERVER, "qpe/getTagData?mode=json&format=defaultInfo"
)
config_url = urlparse.urljoin(QPE_SERVER, "qpe/configureTag")
group_url = urlparse.urljoin(QPE_SERVER, "/qpe/setTagGroup")

################# Query Parameters #################
# the name of the configuration in the project to configure with
CONFIG_ID = "ASSET_TAG"
CHANNEL = "37"  # options are 37 BLE or 230 QProprietary
TARGET_GROUP_NAME = "AutoConfiguredTags"


def update_url_query(url: str, query_params: dict) -> str:
    """takes a url and query string params and returns a new url with those query parameters in it

    Args:
        url (String): original url
        params (dict): query string parameters

    Returns:
        String: new url including query string parameters
    """
    url_parse = urlparse.urlparse(url)
    query = url_parse.query
    url_dict = dict(urlparse.parse_qsl(query))
    url_dict.update(query_params)
    url_new_query = urlparse.urlencode(url_dict)
    url_parse = url_parse._replace(query=url_new_query)
    new_url = urlparse.urlunparse(url_parse)

    return new_url


def main():
    """Main entry point of the app"""

    # initialize the lists of tags in different process states
    unconfigured_tag = []
    config_process_tags = []
    ungrouped_tags = []

    while True:
        # poll QPE for data
        res = requests.get(tag_data_url)
        # make sure response is ok if not sleep and try again
        # it is best to wait some time incase the response did not go through
        # due to network congestion
        if res.status_code != 200:
            time.sleep(3)
            continue

        # this response contains a json array of all tags
        tag_data = res.json()["tags"]

        for tag in tag_data:
            # if tag does not have a group name, it has not been configured,
            # if tag is being/has been configured, ignore.
            if (
                tag["tagGroupName"] is None
                and tag["tagId"] not in config_process_tags
                and tag["tagId"] not in ungrouped_tags
            ):
                unconfigured_tag.append(tag["tagId"])

            # check status for tags undergoing configuration
            elif tag["tagId"] in config_process_tags:
                # possible statuses:
                # aborted, failed, notSupported, waitingToCommand1of3,
                # commanding1of3, commanding2of3, commanding3of3,
                # done, notStarted, waitingForPackets (tag hasn't been seen in a while)
                # the cases handled here are required to function, even minimally, in most use cases
                if tag["configStatus"] == "aborted" or tag["configStatus"] == "failed":
                    # configuration failed, drop from id from list to initiate another attempt
                    unconfigured_tag.append(tag["tagId"])
                    config_process_tags.remove(tag["tagId"])
                elif tag["configStatus"] == "done":
                    ungrouped_tags.append(tag["tagId"])
                    config_process_tags.remove(tag["tagId"])

        print()
        print("Unconfigured IDs:")
        pprint(unconfigured_tag)
        print("In Process IDs:")
        pprint(config_process_tags)
        print("Ungrouped IDs:")
        pprint(ungrouped_tags)

        ################### Request tags to be configured #################
        if len(unconfigured_tag) > 0:
            # build the configure request url
            query_parameters = {
                "tag": ",".join(unconfigured_tag),  # comma separated string of tag ids
                "channel": CHANNEL,  # the tags target channel
                "id": CONFIG_ID,  # id of the configuration in the project
            }
            conf_req = update_url_query(config_url, query_parameters)
            res = requests.get(conf_req)

            if res.status_code == 200:
                # configuration request was successful
                config_process_tags += unconfigured_tag

            unconfigured_tag = []

            pprint(res.json())

        ################# Request tags to be added to group #################
        if len(ungrouped_tags) > 0:
            query_parameters = {
                "tag": ",".join(ungrouped_tags),  # comma separated string of tag ids
                "targetGroup": TARGET_GROUP_NAME,  # the tags target group
            }
            group_req = update_url_query(group_url, query_parameters)
            res = requests.get(group_req)

            if res.status_code == 200:
                # add to group request was successful
                ungrouped_tags = []

            pprint(res.json())

        time.sleep(3)


if __name__ == "__main__":
    main()
