from flask import Flask
from flask import render_template,flash,redirect,request,url_for,send_from_directory,Response
from flask import after_this_request
import subprocess
import sys
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import send_file
import os
from downloader import queryDownload
import argparse
import zipfile
import concurrent
# UPLOAD_FOLDER = '/mnt/c/Users/Ayushmaan/Desktop/Song_Downloader/Songs'
UPLOAD_FOLDER = os.path.join(os.getcwd(),'Songs')

app = Flask(__name__)
#app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
uploads = os.path.join(app.root_path,app.config['UPLOAD_FOLDER'])

def searchAndDownload(processed_text,partial_filename,UPLOAD_FOLDER):
    for filename in os.listdir(UPLOAD_FOLDER):
        if partial_filename in filename:    
            print("Filename returned is",filename)
            return filename
        if partial_filename.upper() in filename.upper():
            print("Filename returned is",filename)
            return filename
        if processed_text in filename.upper():
            print("Filename returned is",filename)
            return filename

def song_api_mulitple(songname):
    partial_filename = queryDownload(songname)
    print(partial_filename)
    song_name = "{}.mp3".format(partial_filename)
    if song_name not in os.listdir(UPLOAD_FOLDER):
        print("HERE PLEASE HELP")
        return searchAndDownload(songname,partial_filename,UPLOAD_FOLDER)
    else:
        print("NO HELP")
        return song_name


@app.route('/song/<songname>')
def song_api(songname):
    partial_filename = queryDownload(songname)
    print(partial_filename)
    song_name = "{}.mp3".format(partial_filename)
    if song_name not in os.listdir(UPLOAD_FOLDER):
        print("HERE PLEASE HELP")
        return send_from_directory(directory=uploads,filename=searchAndDownload(songname,partial_filename,UPLOAD_FOLDER),as_attachment=True)
    else:
        print("NO HELP")
        return send_from_directory(directory=uploads,filename=song_name,as_attachment=True)

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
    #print(processed_text)

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

    return render_template("index.html")


if __name__ == "__main__":
	app.debug=True
	app.run(threaded=True)