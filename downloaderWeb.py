#!/usr/bin/python
from __future__ import unicode_literals
import os
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

def queryWebDownload(video_link):
    video_url = "https://www.youtube.com/watch?v={}".format(video_link)
    print(ydl_opts["outtmpl"])
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    # ydl.download([main_url])
