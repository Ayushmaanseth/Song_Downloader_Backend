# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from pprint import pprint

def youtubeSearch(query):
    song_query = "{} lyrics".format(query)
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyDuHEwPWR6rknnpuSbxpm6Ra4ifSeZBULM"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

    request = youtube.search().list(
        part="snippet",
        maxResults=5,
        q=song_query
    )
    response = request.execute()
    # print([[response["items"][i]["id"]["videoId"], response["items"][i]["snippet"]["title"]] for i in range(5)])
    # pprint(response)
    return response

# youtubeSearch("Remember the name")
