from flask import Flask
from flask_cors import CORS, cross_origin
from flask import render_template,flash,redirect,request,url_for,send_from_directory,Response
from flask import after_this_request,make_response,jsonify
import subprocess
import sys
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import send_file
import os
from downloader import queryDownload, searchVideos, queryDownloadWithSelection
import argparse
import concurrent
from difflib import get_close_matches

UPLOAD_FOLDER = os.path.join(os.getcwd(),'Songs')
app = Flask(__name__)
#app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
uploads = os.path.join(app.root_path,app.config['UPLOAD_FOLDER'])

def searchAndDownload(processed_text,partial_filename,uploadFolder):
    filenames = os.listdir(uploadFolder)
    firstMatch = get_close_matches(partial_filename,filenames)
    if len(firstMatch) > 0:
        return firstMatch[0]
    if len(get_close_matches(processed_text,filenames)) > 0:
        return get_close_matches(processed_text)[0]

    for filename in filenames:
        if partial_filename in filename:    
            print("Filename returned is",filename)
            return filename
        if partial_filename.upper() in filename.upgutper():
            print("Filename returned is",filename)
            return filename
        if processed_text in filename.upper():
            print("Filename returned is",filename)
            return filename
        if partial_filename.split('|')[0].upper() in filename.upper():
            print("Filename returned is",filename, "block is split")
            return filename


def song_api_mulitple(songname):
    partial_filename = queryDownload(songname)
    print(partial_filename)
    song_name = "{}.mp3".format(partial_filename)
    if song_name not in os.listdir(UPLOAD_FOLDER):
        print("HERE PLEASE HELP")
        return searchAndDownload(songname,partial_filename,uploads)
    else:
        print("NO HELP")
        return song_name

@app.route('/songDetail/<songname>')
def song_api_name(songname):
    (title,video_link) = searchVideos("{} lyrics".format(songname))
    response = jsonify(title)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/songDownload/',methods=['POST'])
def song_api_download():
    data = request.get_json()
    title,video_link,selection = data['title'],data['video_link'],data['selection']
    songTitle = queryDownloadWithSelection(title,video_link,selection)
    return send_from_directory(directory=uploads,filename=searchAndDownload(songTitle,songTitle,uploads),as_attachment=True)
    # response.headers['Access-Control-Allow-Origin'] = '*'
    # return response

@app.route('/song/<songname>')
def song_api(songname):
    partial_filename = queryDownload(songname)
    print(partial_filename)
    song_name = "{}.mp3".format(partial_filename)
    if song_name not in os.listdir(UPLOAD_FOLDER):
        print("HERE PLEASE HELP")
        response = send_from_directory(directory=uploads,filename=searchAndDownload(songname,partial_filename,uploads),as_attachment=True)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    else:
        print("NO HELP")
        response = send_from_directory(directory=uploads,filename=song_name,as_attachment=True)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/file/<filename>')
def file_api(filename):
    return send_from_directory(directory=uploads,filename=filename,as_attachment=True)

@app.route('/')
def my_form():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.upper()
    download_text = processed_text
    return song_api(download_text)

@app.route('/multiple')
def multiple():
    return render_template('multiple.html')

    
@app.route('/multiple',methods=['POST'])
def multipleDownloads():
    processed_text = request.form['text']
    processed_text = processed_text.split(',')
    processed_text = list(map(str.upper,processed_text))
    processed_text = list(map(str.strip,processed_text))
    executor = concurrent.futures.ProcessPoolExecutor(4)
    futures = [executor.submit(song_api_mulitple, item) for item in processed_text]
    concurrent.futures.wait(futures)
    return render_template("index.html")


if __name__ == "__main__":
	app.debug=True
	app.run(threaded=True)