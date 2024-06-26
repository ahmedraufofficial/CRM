from operator import ge
from flask import Blueprint, render_template, request, redirect, url_for,jsonify,abort
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import Contacts, User, Contactsdubai
from forms import AddContactForm, AddContactDubaiForm
import json
from functions import logs
import os 
import csv
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
from flask_httpauth import HTTPTokenAuth
from sqlalchemy.orm import sessionmaker

auth = HTTPTokenAuth(scheme='Bearer')
tokens = {
    ''
}

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


@auth.verify_token
def verify_token(token):
    if token in tokens:
        return token
    
@handlecontacts.route('/contacts',methods = ['GET','POST'])
@login_required
def display_contacts():
    if current_user.contact == False or current_user.abudhabi == False:
        return abort(404)
    data = []
    f = open('contacts_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('contacts.html', data = data , columns = columns, vibes = 'ad')

@handlecontacts.route('/fetch_token',methods = ['GET','POST'])
@login_required
def fetch_token():
    return(jsonify(''))

@handlecontacts.route('/fetch_contacts/<user>',methods = ['GET','POST'])
@auth.login_required
def fetch_contacts(user):
    voltage_user = db.session.query(User).filter_by(username = user).first()
    search = request.args.get('search')
    offset = int(request.args.get('offset'))
    limit = int(request.args.get('limit'))
    role = request.args.get('role')
    agent = request.args.get('agent')
    total_records = 0
    data = []
    query = db.session.query(Contacts).filter(or_(Contacts.created_by == voltage_user.username,Contacts.assign_to == voltage_user.username, voltage_user.is_admin == True, voltage_user.listing == True, voltage_user.qa == True))
    if search:
        conditions = [column.ilike(f"%{search}%") for column in Contacts.__table__.columns]
        query = query.filter(or_(*conditions))
    if role or agent:
        filters = []
        if role:
            filters.append(Contacts.role == role)
        if agent:
            filters.append(Contacts.assign_to == agent)
        query = query.filter(and_(*filters))
    z = query.count()
    for r in query.order_by(Contacts.id.desc()).offset(offset).limit(limit):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        for k in ['alternate_number','comment','contact_type','created_by','date_of_birth','language','gender','nationality','religion','role','source','title']: new.pop(k)
        new["edit"] = "<div style='display:flex;'>"+'<a href="/edit_contact/'+str(new['id'])+'"><button  class="btn btn-primary si">Edit</button></a><a href="/delete_contact/'+str(new['id'])+'"><button class="btn btn-danger si">Delete</button></a>'+"</div>"
        new["id"] = total_records
        data.append(new)
        total_records += 1
    response_data = {"total": z, "totalNotFiltered": z, "rows": data}
    return(response_data)

@handlecontacts.route('/add_contact', methods = ['GET','POST'])
@login_required
def add_contact():
    if current_user.contact == False or current_user.abudhabi == False:
        return abort(404) 
    form = AddContactForm()
    if request.method == 'POST': 
        first_name = form.first_name.data
        last_name = form.last_name.data
        number = form.number.data
        check = db.session.query(Contacts).filter_by(number = number).first()
        if check:
            return("<body style='background-color: rgb(204, 8, 8);'><p style='font-family: Arial; text-align: center; margin-top: 50vh; color: white;'>Integrity Error: Number already exists under the User - "+check.assign_to+"<a style='display:block; margin-top: 10px' href='/add_contact'><button  style='background-color: rgb(5, 179, 231); color: white; border: none; padding: 5px;cursor: pointer;'>Back</button></a><a style='display:block; margin-top: 30px;' href='/contacts'><button  style='background-color: rgb(105, 103, 103); color: white; border: none; padding: 5px;cursor: pointer; '>All Contacts</button></a></p></body>")
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
    return render_template('add_contact.html', form=form,user = current_user.username, vibes = 'ad')

@handlecontacts.route('/add_contact/quick_add', methods = ['GET','POST'])
@login_required
def quick_add(): 
    if current_user.contact == False:
        return abort(404) 
    if request.method == 'POST': 
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        number = request.form['number']
        check = db.session.query(Contacts).filter_by(number = number).first()
        if check:
            return jsonify(success=False, name=check.assign_to)
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
    if current_user.contact == False or current_user.edit == False or current_user.abudhabi == False:
        return abort(404) 
    edit = db.session.query(Contacts).filter_by(id=variable).first()
    form = AddContactForm(obj = edit)
    if request.method == 'POST': 
        form.populate_obj(edit)
        db.session.commit()
        logs(current_user.username,edit.refno,'Edited')
        return redirect(url_for('handlecontacts.display_contacts'))
    return render_template('add_contact.html', form=form, assign = current_user.username,user = current_user.username)

@handlecontacts.route('/reassign_contacts69/<personA>/<personB>/<personC>/<personD>/<personE>/<personF>/<personG>/<personH>/<personI>/<personJ>') #lesssgooo
@login_required
def reassign_contacts69(personA,personB,personC,personD,personE,personF,personG,personH,personI,personJ):
    all_contacts = db.session.query(Contacts).filter(or_(Contacts.assign_to == personA,Contacts.assign_to == personB,Contacts.assign_to == personC,Contacts.assign_to == personD,Contacts.assign_to == personE,Contacts.assign_to == personF,Contacts.assign_to == personG,Contacts.assign_to == personH,Contacts.assign_to == personI))
    for i in all_contacts:
        i.assign_to = personJ
        db.session.commit()
    return "ok"

@handlecontacts.route('/delete_contact/<variable>', methods = ['GET','POST'])
@login_required
def delete_contacts(variable):
    if current_user.contact == False or current_user.edit == False or current_user.abudhabi == False:
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

# dubai - contacts

@handlecontacts.route('/contactsdxb',methods = ['GET','POST'])
@login_required
def display_contactsdxb():
    if current_user.contact == False or current_user.dubai == False:
        return abort(404)
    data = []
    f = open('contacts_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('contacts.html', data = data , columns = columns, vibes = 'dxb')

@handlecontacts.route('/fetch_contactsdxb/<user>',methods = ['GET','POST'])
@auth.login_required
def fetch_contactsdxb(user):
    voltage_user = db.session.query(User).filter_by(username = user).first()
    search = request.args.get('search')
    offset = int(request.args.get('offset'))
    limit = int(request.args.get('limit'))
    role = request.args.get('role')
    agent = request.args.get('agent')
    total_records = 0
    data = []

    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    query = session.query(Contactsdubai).filter(or_(Contactsdubai.created_by == voltage_user.username,Contactsdubai.assign_to == voltage_user.username, voltage_user.is_admin == True, voltage_user.qa == True))

    if search:
        conditions = [column.ilike(f"%{search}%") for column in Contactsdubai.__table__.columns]
        query = query.filter(or_(*conditions))
    if role or agent:
        filters = []
        if role:
            filters.append(Contactsdubai.role == role)
        if agent:
            filters.append(Contactsdubai.assign_to == agent)
        query = query.filter(and_(*filters))
    z = query.count()
    for r in query.order_by(Contactsdubai.id.desc()).offset(offset).limit(limit):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        for k in ['alternate_number','comment','contact_type','created_by','date_of_birth','language','gender','nationality','religion','source','title']: new.pop(k)
        new["edit"] = "<div style='display:flex;'>"+'<a href="/edit_contactdxb/'+str(new['refno'])+'"><button  class="btn btn-primary si">Edit</button></a><a href="/delete_contactdxb/'+str(new['refno'])+'"><button class="btn btn-danger si">Delete</button></a>'+"</div>"
        new["id"] = total_records
        data.append(new)
        total_records += 1
    response_data = {"total": z, "totalNotFiltered": z, "rows": data}
    session.close()
    return(response_data)

@handlecontacts.route('/add_contactdxb', methods = ['GET','POST'])
@login_required
def add_contactdxb():
    if current_user.contact == False or current_user.dubai == False:
        return abort(404) 
    form = AddContactDubaiForm()
    if request.method == 'POST': 
        Session = sessionmaker(bind=db.get_engine(bind='fourth'))
        session = Session()
        first_name = form.first_name.data
        last_name = form.last_name.data
        number = form.number.data
        check = session.query(Contactsdubai).filter_by(number = number).first()
        if check:
            return("<body style='background-color: rgb(204, 8, 8);'><p style='font-family: Arial; text-align: center; margin-top: 50vh; color: white;'>Integrity Error: Number already exists under the User - "+check.assign_to+"<a style='display:block; margin-top: 10px' href='/add_contact'><button  style='background-color: rgb(5, 179, 231); color: white; border: none; padding: 5px;cursor: pointer;'>Back</button></a><a style='display:block; margin-top: 30px;' href='/contacts'><button  style='background-color: rgb(105, 103, 103); color: white; border: none; padding: 5px;cursor: pointer; '>All Contacts</button></a></p></body>")
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
        branch = form.branch.data
        newcontact = Contactsdubai(first_name=first_name, last_name=last_name ,number=number,alternate_number=alternate_number,contact_type=contact_type,role=role,nationality=nationality,source=source,assign_to=assign_to,email=email,title=title,gender=gender,religion=religion,date_of_birth=date_of_birth,language=language,comment=comment,branch=branch, created_by = current_user.username)
        session.add(newcontact)
        session.commit()
        session.refresh(newcontact)
        newcontact.refno = 'UNI-CD-'+str(newcontact.id)
        session.commit()
        logs(current_user.username,'UNI-CD-'+str(newcontact.id),'Added')
        session.close()
        return redirect(url_for('handlecontacts.display_contactsdxb'))
    return render_template('add_contact.html', form=form,user = current_user.username, vibes = 'dxb')

@handlecontacts.route('/edit_contactdxb/<variable>', methods = ['GET','POST'])
@login_required
def edit_contactdxb(variable):
    if current_user.contact == False or current_user.edit == False or current_user.dubai == False:
        return abort(404) 
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    edit = session.query(Contactsdubai).filter_by(refno=variable).first()
    form = AddContactDubaiForm(obj = edit)
    if request.method == 'POST': 
        form.populate_obj(edit)
        session.commit()
        logs(current_user.username,edit.refno,'Edited')
        session.close()
        return redirect(url_for('handlecontacts.display_contactsdxb'))
    session.close()
    return render_template('add_contact.html', form=form, assign = current_user.username,user = current_user.username, vibes = 'dxb')

@handlecontacts.route('/delete_contactdxb/<variable>', methods = ['GET','POST'])
@login_required
def delete_contactsdxb(variable):
    if current_user.contact == False or current_user.edit == False  or current_user.dubai == False:
        return abort(404) 
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    delete = session.query(Contactsdubai).filter_by(refno=variable).first()
    session.delete(delete)
    session.commit()
    session.close()
    return redirect(url_for('handlecontacts.display_contactsdxb'))