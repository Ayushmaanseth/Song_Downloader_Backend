#!/usr/bin/python
from __future__ import unicode_literals
import os
import sys
import requests
from bs4 import BeautifulSoup
import re
import youtube_dl
from urllib.error import HTTPError

class MyLogger(object):
  def debug(self, msg):
    pass

  def warning(self, msg):
    pass

  def error(self, msg):
    print(msg)


def my_hook(d):

  if d['status'] == 'finished':
    print('Done downloading, now converting ...')
# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl':'Songs/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '96',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

DEVELOPER_KEY = "AIzaSyBydcQn0HgnCImskEyN25UQa7wit-3I6gM"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def extract_videos(html):
    """
    Parses given html and returns a list of (Title, Link) for
    every movie found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    pattern = re.compile(r'/watch\?v=')
    found = soup.find_all('a', 'yt-uix-tile-link', href=pattern)
    return [(x.text.encode('utf-8'), x.get('href')) for x in found]

def makeRequest(url, hdr):
    http_proxy  = os.environ.get("HTTP_PROXY")
    https_proxy = os.environ.get("HTTPS_PROXY")
    ftp_proxy   = os.environ.get("FTP_PROXY")

    proxyDict = { 
        "http"  : http_proxy,
        "https" : https_proxy,
        "ftp"   : ftp_proxy
        }

    req = requests.get(url, headers=hdr, proxies=proxyDict)
    return req

def searchVideos(query):
    """
    Searches for videos given a query
    """
    response = makeRequest('https://www.youtube.com/results?search_query=' + query, {})
    print("Request made...")
    return extract_videos(response.content)

def youtube_search(song_name):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)
  
  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=song_name,
    part="id,snippet",
    maxResults=1
  ).execute()

  videos = []
  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videos.append("%s" % (search_result["id"]["videoId"]))

  temp_url = "https://www.youtube.com/watch?v="
  download_url = temp_url + videos[0]

  # command = 'youtube-dl -cit --no-warnings --extract-audio --audio-quality 0 --audio-format mp3 ' + download_url
  # print(download_url)
  # os.system(command)

  #delete_command = 'del /S *.jpg'
  #os.system(delete_command)


  #print (videos[0])
  #print ("Channels:\n", "\n".join(channels), "\n")
  #print ("Playlists:\n", "\n".join(playlists), "\n")
  return download_url

def queryDownload(song_name):
  available = searchVideos("{} lyrics".format(song_name))
  title,video_link = available[0]
  # song_name_mp3 = title.decode() + '.mp3'
  # main_url = youtube_search(song_name)
  # print("Downloading now...",title.decode().split('|')[0])
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com' + video_link])
    # ydl.download([main_url])
  # print(title.decode())
  # print(title.decode().split('|')[0])
  return title.decode()





if __name__ == "__main__":

  f = open('songs.txt','r')
  song_names = f.readlines()
  
  print("Songs are ",song_names)
  for song_name in song_names:
    print(song_name)
    if len(song_name) > 1 and song_name is not None and song_name != '' and song_name != "" and song_name != " " and song_name != ' ':
      print("Downloading ",len(song_name))
      #argparser.add_argument("--q", help="Search term", default="Google")
      #rgparser.add_argument("--max-results", help="Max results", default=1)
      #args = argparser.parse_args()

      try:
        #youtube_search(song_name + "full song")
        
        queryDownload(song_name + " full song lyrics")
      except (HTTPError, e):
        print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        continue
      except Exception as e:
        print("Exception {} occured, please try again :(".format(e))
        continue

    else:
      #print("Wrong name")
      break
      #sys.exit(0)



