from flask import Flask
from flask import render_template,flash,redirect,request,url_for,send_from_directory, Response
import subprocess
import sys
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import send_file
import os
from downloader import queryDownload
import argparse
import zipfile
from downloaderWeb import queryWebDownload
from youtube import youtubeSearch
import html
import concurrent
from requests_toolbelt import MultipartEncoder
# UPLOAD_FOLDER = '/mnt/c/Users/Ayushmaan/Desktop/Song_Downloader/Songs'
UPLOAD_FOLDER = os.path.join(os.getcwd(),'Songs')

app = Flask(__name__)
#app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
uploads = os.path.join(app.root_path,app.config['UPLOAD_FOLDER'])

def searchAndDownload(processed_text,partial_filename,UPLOAD_FOLDER):
    for filename in os.listdir(UPLOAD_FOLDER):
        if partial_filename in filename:    
            print(partial_filename)
            print("Here")
            return filename
        if partial_filename.upper() in filename.upper():
            print("Here3")
            return filename
        if processed_text in filename.upper():
            print("Here2")
            return filename

def song_api_mulitple(songname):
    print("Request made")
    response = youtubeSearch(songname) 
    title,video_link = response["items"][0]["snippet"]["title"], response["items"][0]["id"]["videoId"]
    title = html.unescape(title)
    print(title)
    queryWebDownload(video_link)
    return title

@app.route('/')
def my_form():
    return render_template('index.html')

@app.route('/multiple')
def multiple():
    return render_template('multiple.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    return song_api(text)   

@app.route('/file/<filename>')
def post_file(filename):
    # processed_text = filename.upper()
    # partial_filename = queryDownload(processed_text)
    # print(partial_filename)
    return send_from_directory(directory=uploads,filename=searchAndDownload(filename),as_attachment=True)

@app.route('/songs/<songname>')
def song_api(songname):
    print("Request made")
    response = youtubeSearch(songname) 
    title,video_link = response["items"][0]["snippet"]["title"], response["items"][0]["id"]["videoId"]
    title = html.unescape(title)
    print(title)
    queryWebDownload(video_link)
    return send_from_directory(directory=uploads,filename="{}.mp3".format(title),as_attachment=True)

@app.route('/multiple',methods=['POST'])
def multipleDownloads():
    processed_text = request.form['text']
    processed_text = processed_text.split(',')
    processed_text = list(map(str.upper,processed_text))
    executor = concurrent.futures.ProcessPoolExecutor(4)
    futures = [executor.submit(song_api_mulitple, item) for item in processed_text]
    concurrent.futures.wait(futures)
    # zipf = zipfile.ZipFile('Songs.zip','w')
    # for file in processed_text:
    #     file = file.upper()
    #     partial_filename = queryDownload(file)
    #     filename = searchAndDownload(file,partial_filename,UPLOAD_FOLDER)
    #     filepath = os.path.join(UPLOAD_FOLDER,filename)
    #     zipf.write(filepath)
    # zipf.close()

    # return send_file('Songs.zip',
    #                 mimetype='zip',
    #                 attachment_filename='Songs.zip',
    #                 as_attachment=True)
    # send_from_directory(directory=uploads,filename="{}.mp3".format(processed_text[0]),as_attachment=True)
    # m = MultipartEncoder({
    #        'field1': (os.path.join(uploads,"{}.mp3".format(futures[0].result()))),
    #        'field2': (os.path.join(uploads,"{}.mp3".format(futures[1].result())))
    #     })
    # return Response(m,mimetype=m.content_type)
    return render_template("index.html")

    
if __name__ == "__main__":
	app.run(threaded=True,debug=True)