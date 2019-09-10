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

def my_hook(d):
  if d['status'] == 'finished':
    print('Done downloading, now converting ...')

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl':'Songs/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '64',
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}


def extract_videos(html):
    """
    Parses given html and returns a list of (Title, Link) for
    every movie found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    pattern = re.compile(r'/watch\?v=')
    found = soup.find('a', 'yt-uix-tile-link', href=pattern)
    firstFound = found
    # return [(x.text.encode('utf-8'), x.get('href')) for x in found]
    return (firstFound.text.encode('utf-8'), firstFound.get('href'))

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

def queryDownload(song_name):
  available = searchVideos("{} lyrics".format(song_name))
  (title,video_link) = available
  
  with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com' + video_link])
    
  return title.decode()

  
def queryDownloadWithSelection(song_name,selection):
  available = searchVideos("{} lyrics".format(song_name))
  (title,video_link) = available
  ydl_opts_with_selection = {
    'format': 'bestaudio/best',
    'outtmpl':'Songs/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': selection,
    }],
    'logger': MyLogger(),
    'progress_hooks': [my_hook],
}

  with youtube_dl.YoutubeDL(ydl_opts_with_selection) as ydl:
    ydl.download(['https://www.youtube.com' + video_link])
    
  return title.decode()


# Main function just for testing purposes
if __name__ == "__main__":

  f = open('songs.txt','r')
  song_names = f.readlines()
  print("Songs are ",song_names)
  for song_name in song_names:
    print(song_name)
    if len(song_name) > 1 and song_name is not None and song_name != '' and song_name != "" and song_name != " " and song_name != ' ':
      print("Downloading ",len(song_name))
      try:
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



