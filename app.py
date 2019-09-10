from flask import Flask
from flask_cors import CORS, cross_origin, jsonify
from flask import render_template,flash,redirect,request,url_for,send_from_directory,Response
from flask import after_this_request,make_response
import subprocess
import sys
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import send_file
import os
from downloader import queryDownload, searchVideos
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
    return get_close_matches(partial_filename,filenames)[0]

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