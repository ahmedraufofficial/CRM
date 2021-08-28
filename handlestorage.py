from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort,send_file, send_from_directory
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import Properties
from forms import AddFile
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
import glob
from functions import logs, notes, add_user_list
from sqlalchemy import or_
import pyAesCrypt
import io
from os import stat
import os.path
import shutil



a = os.getcwd()
UPLOAD_FOLDER = os.path.join(a+'/static', 'cloudstorage')
UPLOAD_FORM = os.path.join(a+'/static', 'forms')

db = SQLAlchemy()

handlestorage = Blueprint('handlestorage', __name__, template_folder='templates')

@handlestorage.route('/cloudstorage',methods = ['GET','POST'])
@login_required
def cloudstorage():
    return render_template('cloudstorage.html')


@handlestorage.route('/cloudstorage/files',methods = ['GET','POST'])
@login_required
def display_storage():
    path = UPLOAD_FOLDER+'/'+current_user.username
    user_directory = os.path.isdir(path)
    all = []
    if user_directory:
        header = "Files Available to download"
        files = os.listdir(path)
        for f in files:
            all.append(f)
    else:
        header = "No File Received"


    form = AddFile()
    if request.method == 'POST':
        bufferSize = 128 * 1024
        password = form.password.data
        send = form.send.data
        for filex in form.files.data:
            file_filename = secure_filename(filex.filename)
            directory = UPLOAD_FOLDER+'/'+send
            if not os.path.isdir(directory):
                os.mkdir(directory)
            pbdata = filex.stream.read()
            fIn = io.BytesIO(pbdata)
            fCiph = io.BytesIO()
            pyAesCrypt.encryptStream(fIn, fCiph, password, bufferSize)
            with open(directory + "/"+file_filename+'.aes','wb') as out:
                out.write(fCiph.getvalue()) 
            return render_template('filestorage.html', form = form, all_files = all, header = header) 

    return render_template('filestorage.html', form = form, all_files = all, header = header)
  



@handlestorage.route('/upload/<password>/<path:file_filename>', methods=['GET', 'POST'])
def download(password,file_filename):
    bufferSize = 128 * 1024
    directory = UPLOAD_FOLDER +'/'+current_user.username
    encFileSize = stat(directory + "/"+file_filename).st_size
    fOut = io.BytesIO()
    with open(directory + "/"+file_filename, "rb") as fIn:
        name,ext,enc = file_filename.split('.')
        try:
            pyAesCrypt.decryptStream(fIn, fOut, password, bufferSize, encFileSize)
            filetype = {'csv': 'text/csv', 'doc': 'application/msword', 'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'gz': 'application/gzip', 'mp4': 'video/mp4', 'png': 'image/png', 'pdf': 'application/pdf', 'ppt': 'application/vnd.ms-powerpoint', 'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'txt': 'text/plain', 'webp': 'image/webp', 'jpg': 'image/jpg', 'jpeg': 'image/jpeg'}
            mem = io.BytesIO()
            mem.write(fOut.getbuffer())
            mem.seek(0)
            return send_file(mem,attachment_filename=name+"."+ext,mimetype=filetype[ext], as_attachment=True)
        except:
            return redirect(url_for('handlestorage.display_storage'))

@handlestorage.route('/emptydirectory', methods=['GET', 'POST'])
def emptydir():
    directory = UPLOAD_FOLDER +'/'+current_user.username
    try:
        shutil.rmtree(directory)
        return jsonify({"success":"200"})
    except:
        return jsonify({"success":"200"})


@handlestorage.route('/cloudstorage/forms', methods=['GET', 'POST'])
def allforms():
    all = []
    forms = os.listdir(UPLOAD_FORM)
    for f in forms:
        all.append(f)
    if request.method == 'POST':
        file = request.files['file']
        file_filename = secure_filename(file.filename)
        directory = UPLOAD_FOLDER+'/hr'
        if not os.path.isdir(directory):
            os.mkdir(directory)
        file.save(os.path.join(directory, file_filename))
    return render_template('formstorage.html', all_forms=all)

@handlestorage.route('/cloudstorage/forms/<path:filename>', methods=['GET', 'POST'])
def getform(filename): 
    try:
        return send_from_directory(UPLOAD_FORM, filename=filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@handlestorage.route('/cloudstorage/hr', methods=['GET', 'POST'])
def hrforms():
    if current_user.hr == False:
        return abort(404)
    else:
        all = []
        try:
            forms = os.listdir(UPLOAD_FOLDER+'/hr')
        except FileNotFoundError:
            os.mkdir(UPLOAD_FOLDER+'/hr')
            forms = os.listdir(UPLOAD_FOLDER+'/hr')
        for f in forms:
            all.append(f)
        return render_template('hrstorage.html', all_files=all)

@handlestorage.route('/cloudstorage/hr/<path:filename>', methods=['GET', 'POST'])
def gethrforms(filename):
    if current_user.hr == False:
        return abort(404)
    else:
        try:
            return send_from_directory(UPLOAD_FOLDER + '/hr', filename=filename, as_attachment=True)
        except FileNotFoundError:
            abort(404)

@handlestorage.route('/cloudstorage/hr/emptydirectory', methods=['GET', 'POST'])
def hremptydir():
    if current_user.hr == False:
        return abort(404)
    else:
        directory = UPLOAD_FOLDER +'/hr'
        try:
            shutil.rmtree(directory)
            return jsonify({"success":"200"})
        except:
            return jsonify({"success":"200"})

