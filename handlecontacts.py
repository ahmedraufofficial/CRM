from operator import ge
from flask import Blueprint, render_template, request, redirect, url_for,jsonify,abort
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import Contacts
from forms import AddContactForm
import json
from functions import logs
import os 
import csv
import arabic_reshaper
from bidi.algorithm import get_display
from sqlalchemy import or_
from datetime import datetime, timedelta


a = os.getcwd()
UPLOAD_FOLDER = os.path.join(a+'/static', 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


db = SQLAlchemy()

handlecontacts = Blueprint('handlecontacts', __name__, template_folder='templates')

def write_json(new_data, filename='contacts.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data["contacts"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def new_value():
    try:
        new_entry = db.session.query(Contacts).order_by(Contacts.id.desc()).first()
    except: 
        new_entry = db.session.query(Contacts).first()
    new_data = {"id": str(new_entry.id) , "name" : str(new_entry.first_name + ' ' + new_entry.last_name)}
    write_json(new_data)


        
@handlecontacts.route('/contacts',methods = ['GET','POST'])
@login_required
def display_contacts():
    if current_user.contact == False:
        return abort(404)
    data = []
    for r in db.session.query(Contacts).filter(or_(Contacts.created_by == current_user.username,Contacts.assign_to == current_user.username, current_user.is_admin == True)):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        for k in []: new.pop(k)
        new["edit"] = "<div style='display:flex;'>"+'<a href="/edit_contact/'+str(new['id'])+'"><button  class="btn btn-primary si">Edit</button></a><a href="/delete_contact/'+str(new['id'])+'"><button class="btn btn-danger si">Delete</button></a>'+"</div>"
        data.append(new)
    #with open('contacts.json', 'w') as fout:
    #    json.dump(data , fout)
    f = open('contacts_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('contacts.html', data = data , columns = columns)


@handlecontacts.route('/add_contact', methods = ['GET','POST'])
@login_required
def add_contact():
    if current_user.contact == False:
        return abort(404) 
    form = AddContactForm()
    if request.method == 'POST': 
        first_name = form.first_name.data
        last_name = form.last_name.data
        number = form.number.data
        alternate_number = form.alternate_number.data
        contact_type = form.contact_type.data
        role = form.role.data
        nationality = form.nationality.data
        source = form.source.data
        assign_to = form.assign_to.data
        email = form.email.data
        title = form.title.data
        gender = form.gender.data
        date_of_birth = form.date_of_birth.data
        religion = form.religion.data
        language = form.language.data
        comment = form.comment.data
        newcontact = Contacts(first_name=first_name, last_name=last_name ,number=number,alternate_number=alternate_number,contact_type=contact_type,role=role,nationality=nationality,source=source,assign_to=assign_to,email=email,title=title,gender=gender,religion=religion,date_of_birth=date_of_birth,language=language,comment=comment)
        db.session.add(newcontact)
        db.session.commit()
        db.session.refresh(newcontact)
        newcontact.refno = 'UNI-O-'+str(newcontact.id)
        db.session.commit()
        directory = UPLOAD_FOLDER+'/UNI-O-'+str(newcontact.id)
        if not os.path.isdir(directory):
            os.mkdir(directory)
        logs(current_user.username,'UNI-O-'+str(newcontact.id),'Added')
        return redirect(url_for('handlecontacts.display_contacts'))
    return render_template('add_contact.html', form=form,user = current_user.username)

@handlecontacts.route('/add_contact/quick_add', methods = ['GET','POST'])
@login_required
def quick_add(): 
    if current_user.contact == False:
        return abort(404) 
    if request.method == 'POST': 
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        number = request.form['number']
        email = request.form['email']
        newcontact = Contacts(first_name=first_name, last_name=last_name ,number=number,email=email, assign_to=current_user.username)
        db.session.add(newcontact)
        db.session.commit()
        db.session.refresh(newcontact)
        newcontact.refno = 'UNI-O-'+str(newcontact.id)
        db.session.commit()
        directory = UPLOAD_FOLDER+'/UNI-O-'+str(newcontact.id)
        if not os.path.isdir(directory):
            os.mkdir(directory)
        logs(current_user.username,'UNI-O-'+str(newcontact.id),'Added')
        #new_value()
        return jsonify(success=True)

@handlecontacts.route('/edit_contact/<variable>', methods = ['GET','POST'])
@login_required
def edit_contact(variable):
    if current_user.contact == False or current_user.edit == False:
        return abort(404) 
    edit = db.session.query(Contacts).filter_by(id=variable).first()
    form = AddContactForm(obj = edit)
    if request.method == 'POST': 
        form.populate_obj(edit)
        db.session.commit()
        logs(current_user.username,edit.refno,'Edited')
        return redirect(url_for('handlecontacts.display_contacts'))
    return render_template('add_contact.html', form=form, assign = current_user.username,user = current_user.username)

@handlecontacts.route('/delete_contact/<variable>', methods = ['GET','POST'])
@login_required
def delete_contacts(variable):
    if current_user.contact == False or current_user.edit == False:
        return abort(404) 
    delete = db.session.query(Contacts).filter_by(id=variable).first()
    db.session.delete(delete)
    db.session.commit()
    directory = UPLOAD_FOLDER+'/UNI-O-'+str(variable)
    try:
        os.rmdir(directory)
    except OSError as error:
        print(error)
        return("Directory '% s' can not be removed but contact removed, Contact your tech support" % directory)
    return redirect(url_for('handlecontacts.display_contacts'))
    




'''
@handlecontacts.route('/import_contacts', methods = ['GET','POST'])
@login_required
def import_contact():
    with open("contacts.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        user = []
        for row in reader:
            a = (row[0].split(','))
            user.append(a[1:])

        user = user[1:]
        user.reverse()
 
        for i in user:
            fs = arabic_reshaper.reshape(i[1])
            fs = get_display(fs)   
            ls = arabic_reshaper.reshape(i[2])
            ls = get_display(ls)   
            try:
                newcontact = Contacts(first_name=fs, last_name=ls ,number=int(float(i[3].replace('- -','0').replace('+','00').replace(' ',''))),alternate_number=int(float(i[6].replace('- -','0').replace('+','00').replace(' ',''))),role=i[12],nationality=i[9],source=i[13],assign_to=i[7].replace(" ","_"),email=i[4],title=i[5],gender=i[0],religion=i[8],language=i[11])
                db.session.add(newcontact)
                db.session.commit()
                db.session.refresh(newcontact)
                newcontact.refno = 'UNI-O-'+str(newcontact.id)
                db.session.commit()
                directory = UPLOAD_FOLDER+'/UNI-O-'+str(newcontact.id)
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                with open('map_contact.json','r+') as file:
                    columns = json.load(file)
                    columns["map_contact"].update({i[14]:newcontact.refno})
                    file.seek(0)
                    json.dump(columns, file,indent=4)
                    file.truncate()
            except:
                pass

        return jsonify(fs)
'''