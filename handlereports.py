from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.elements import Null
from sqlalchemy.util.langhelpers import NoneType
from models import Deals, Leads, Properties, User, Dailyreports
from forms import DailyReport
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import datetime, timedelta
from functions import *
from sqlalchemy import or_, and_

path = os.getcwd()
REPORTS = os.path.join(path, 'static/reports')
if not os.path.isdir(REPORTS):
    os.mkdir(REPORTS)

db = SQLAlchemy()

handlereports = Blueprint('handlereports', __name__, template_folder='templates')

@handlereports.route('/dailyreports',methods = ['GET','POST'])
@login_required
def display_reports():   
    if current_user.sale == False:
        return abort(404)
    data = []
    tareekh = datetime.now()+timedelta(hours=4)
    if current_user.is_admin == True:
        for r in db.session.query(Dailyreports).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            report_note = '<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_report('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'
            new["action"] = "<div style='display:flex;'>"+report_note+delete_btn+"</div>"
            #ye_check = tareekh - datetime.strptime(new['created_date'], '%m/%d/%y %H:%M:%S.%f')
            #print(ye_check)
            data.append(new)
    elif current_user.viewall == True and current_user.team_lead == True:
        for r in db.session.query(Dailyreports).filter(Dailyreports.created_by == current_user.username):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            report_note = '<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_report('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'
            new["action"] = "<div style='display:flex;'>"+report_note+"</div>"
            data.append(new)

        for i in current_user.team_members.split(','):
            for r in db.session.query(Dailyreports).filter(Dailyreports.created_by == i):
                row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
                new = row2dict(r)
                report_note = '<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_report('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'
                new["action"] = "<div style='display:flex;'>"+report_note+"</div>"
                data.append(new)

    elif current_user.sale == True:
        for r in db.session.query(Dailyreports).filter(Dailyreports.created_by == current_user.username):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            report_note = '<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_report('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'
            new["action"] = "<div style='display:flex;'>"+report_note+"</div>"
            data.append(new)

    f = open('report_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).all()
    team_leader = db.session.query(User).filter(User.team_lead == True).all()
    return render_template('daily_reports.html', data = data , columns = columns, user = current_user.username, all_users = all_users, team_leader = team_leader)

@handlereports.route('/add_new_report', methods = ['GET','POST'])
@login_required
def add_new_report():
    if current_user.sale == False:
        return abort(404)  
    form = DailyReport()
    all_sale_users = db.session.query(User).filter_by(sale = True).all()
    if request.method == 'POST':
        client_name = form.client_name.data
        client_number = form.client_number.data
        client_email = form.client_email.data
        bedroom = form.bedrooms.data
        team = form.team_lead.data
        remarks = form.remarks.data
        w = open('abudhabi.json')
        file_data = json.load(w)
        try:
            location = file_data[form.locationtext.data]
        except:
            location = "None"
        community = form.building.data
        created_by = current_user.username
        created_date = datetime.now()+timedelta(hours=4)
        updated_date = datetime.now()+timedelta(hours=4)
        newreport = Dailyreports(client_name=client_name, client_number=client_number,client_email=client_email,bedroom=bedroom,team=team,remarks=remarks,location=location,community=community,created_by=created_by,created_date=created_date,updated_date=updated_date)
        db.session.add(newreport)
        db.session.commit()
        db.session.refresh(newreport)
        newreport.refno = 'D-R-'+str(newreport.id)
        db.session.commit()

        logs(current_user.username,'D-R-'+str(newreport.id),'Added')
        create_report_notes('D-R-' + str(newreport.id))
        a = check_value(client_number)
        update_report('ADMIN', newreport.refno, a, 'In Progress', 'mgmt')
        return redirect(url_for('handlereports.display_reports'))
    return render_template('add_daily_report.html', form=form, user = current_user.username, all_sale_users = all_sale_users)

def create_report_notes(listid):
    with open(os.path.join(REPORTS,listid+'.json'), 'w') as f:
        data = {}
        data['notes'] = []
        json.dump(data, f)

@handlereports.route('/check_value/<fieldValue>',methods = ['GET','POST'])
def check_value(fieldValue):
    my_field_value = fieldValue
    try:
        check = db.session.query(Leads).filter(Leads.contact_number.endswith(my_field_value[-7:])).all()
        if check:
            for i in check:
                comment = 'This client already exists as a LEAD under '+i.agent+'. Reference Number: '+i.refno
            return(comment)
        else:
            comment = 'This is a NEW CLIENT.'
            return(comment)
    finally:
        print('Ye tou done hoo geya')

@handlereports.route('/update_report/<list_id>/<com>/<status>/<substatus>',methods = ['GET','POST'])
@login_required
def lets_comment(list_id, com, status, substatus):
    update_report(current_user.username, list_id, com, status, substatus)
    return jsonify(success=True)

def update_report(username, listid, com, status, substatus):
    username = username.replace("%20"," ")
    com = com.replace("%20"," ")
    substatus = substatus.replace("%20"," ")
    with open(os.path.join(REPORTS, listid+'.json'),'r+') as file:
        columns = json.load(file)
        now = datetime.now()+timedelta(hours=4)
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")
        columns["notes"].append({
            'date':date,
            'time':time,
            'user':username,
            'comment': com,
            'status': status,
            'substatus': substatus
        })
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()
    

@handlereports.route('/getem_report/<variable>',methods = ['GET','POST'])
@login_required
def getem_report(variable):
    notes = get_report(variable)
    all_notes = []
    if current_user.is_admin == True or current_user.team_lead == True:
        for i in notes:
            noteObj = {}
            noteObj['date'] = i['date']
            noteObj['time'] = i['time']
            noteObj['user'] = i['user']
            noteObj['comment'] = i['comment']
            noteObj['status'] = i['status']
            noteObj['substatus'] = i['substatus']
            all_notes.append(noteObj)
    else:
        for i in notes:
            if i['substatus'] == 'agncy':
                noteObj = {}
                noteObj['date'] = i['date']
                noteObj['time'] = i['time']
                noteObj['user'] = i['user']
                noteObj['comment'] = i['comment']
                noteObj['status'] = i['status']
                noteObj['substatus'] = i['substatus']
                all_notes.append(noteObj)
    return jsonify({'notes': all_notes})

def get_report(listid):
    f = open(os.path.join(REPORTS,listid+'.json'))
    columns = json.load(f)
    con = columns["notes"]
    return con