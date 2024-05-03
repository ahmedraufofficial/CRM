from curses.ascii import NUL
from operator import methodcaller
from xml.dom.minicompat import EmptyNodeList
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import except_all
from models import Leads, Maindraft, User, Activedraft, Agentlogs
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import date, datetime,time
from functions import assign_lead, logs, notes, update_note,lead_email, etisy_message, update_lead_note
from sqlalchemy import or_,and_, bindparam
import csv
from datetime import datetime, timedelta
from flask_httpauth import HTTPTokenAuth
from sqlalchemy.orm import sessionmaker
  
auth = HTTPTokenAuth(scheme='Bearer')
tokens = {
    ''
}

db = SQLAlchemy()

handlelogs = Blueprint('handlelogs', __name__, template_folder='templates')

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return token
    
@handlelogs.route('/fetch_logs_token',methods = ['GET','POST'])
@login_required
def fetch_logs_token():
    return(jsonify(''))

def assign_new_draft(user, client_name, client_number):
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    newlog = Agentlogs(user=user, client_name=client_name, client_number=client_number, type='Drafts', status='Assigned', created_date = datetime.now()+timedelta(hours=4))
    session.add(newlog)
    session.commit()
    session.refresh(newlog)
    newlog.refno = 'LOG-'+str(newlog.id)
    session.commit()
    session.close()

def edit_draft_agent(user, client_number, status, details):
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    query = session.query(Agentlogs).filter(and_(Agentlogs.client_number.endswith(client_number[-8:]), Agentlogs.user == user, Agentlogs.status == 'Assigned')).first()
    query.status = status
    query.details = details
    query.updated_date = datetime.now()+timedelta(hours=4)
    session.commit()
    session.close()

def lead_update_log(user, client_name, client_number, status, details):
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    newlog = Agentlogs(user=user, client_name=client_name, client_number=client_number, type='Lead', status=status, details=details, created_date = datetime.now()+timedelta(hours=4))
    session.add(newlog)
    session.commit()
    session.refresh(newlog)
    newlog.refno = 'LOG-'+str(newlog.id)
    session.commit()
    session.close()


@handlelogs.route('/logs/agents',methods = ['GET','POST'])
@login_required
def display_all_drafts():   
    if current_user.is_admin == False:
        return abort(404)
    data = []
    f = open('agentlogs_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    all_sale_users = db.session.query(User).filter_by(sale = True).all()
    return render_template('agents_logs.html', data = data , columns = columns, all_sale_users = all_sale_users)

@handlelogs.route('/fetch_logs',methods = ['GET','POST'])
@auth.login_required
def fetch_drafts():
    search = request.args.get('search')
    offset = int(request.args.get('offset'))
    limit = int(request.args.get('limit'))
    total_records = 0
    data = []
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    query = session.query(Agentlogs)
    if search:
        conditions = [column.ilike(f"%{search}%") for column in Agentlogs.__table__.columns]
        query = query.filter(or_(*conditions))
    
    if request.args.get('filter') == 'ON':
        conditions = []
        filters_01 = {key: request.args.get(key) for key in request.args}
        filters = {key: filters_01[key] for key in ['user', 'type', 'status', 'propdate', 'propdate2'] if key in filters_01}
        for key, value in filters.items():
            if key == 'propdate':
                conditions.append(Agentlogs.created_date >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(Agentlogs.created_date <= value)
            else:
                conditions.append(getattr(Agentlogs, key) == value)
        query = query.filter(and_(*conditions))
    
    z = query.count()
    interested_clients = 0
    no_answer = 0
    lead_lost = 0
    for r in query:
        if r.status == 'Interested':
            interested_clients += 1
        elif r.status == 'No Answer':
            no_answer += 1
        elif r.status == 'Lead Lost':
            lead_lost += 1
        else:
            pass
    for r in query.order_by(Agentlogs.id.desc()).offset(offset).limit(limit):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        new['created_date'] = new['created_date'][:16]
        new['updated_date'] = new['updated_date'][:16]
        data.append(new)
        total_records += 1
    response_data = {"total": z, "totalNotFiltered": z, "rows": data, "interested_clients": interested_clients, "no_answer": no_answer, "lead_lost": lead_lost}
    session.close()
    return(response_data)