from curses.ascii import NUL
from operator import methodcaller
from xml.dom.minicompat import EmptyNodeList
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import except_all
from models import Leads, User, Agentlogs, Leadlogs, Leadslogsdubai, Agentlogsdxb
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import date, datetime,time
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

def assign_new_draft(user, client_name, client_number, branch): # -> Start here
    if branch == 'ad':
        agent_logs = Agentlogs
    elif branch == 'dxb':
        agent_logs = Agentlogsdxb
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    newlog = agent_logs(user=user, client_name=client_name, client_number=client_number, type='Drafts', status='Assigned', created_date = datetime.now()+timedelta(hours=4))
    session.add(newlog)
    session.commit()
    session.refresh(newlog)
    newlog.refno = 'LOG-D-'+str(newlog.id)
    session.commit()
    session.close()

def edit_draft_agent(user, client_number, status, details, branch):
    if branch == 'ad':
        agent_logs = Agentlogs
    elif branch == 'dxb':
        agent_logs = Agentlogsdxb
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    query = session.query(agent_logs).filter(and_(agent_logs.client_number.endswith(client_number[-8:]), agent_logs.user == user, agent_logs.status == 'Assigned')).first()
    query.status = status
    query.details = details
    query.updated_date = datetime.now()+timedelta(hours=4)
    session.commit()
    session.close()

def lead_update_log(user, client_name, client_number, status, source, details):
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    newlog = Leadlogs(user=user, client_name=client_name, client_number=client_number, type='Lead', status=status, details=details, source=source, created_date = datetime.now()+timedelta(hours=4))
    session.add(newlog)
    session.commit()
    session.refresh(newlog)
    newlog.refno = 'LOG-L-'+str(newlog.id)
    session.commit()
    session.close()

def edit_lead_agent(user, client_number):
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    query = session.query(Leadlogs).filter(and_(Leadlogs.client_number.endswith(client_number[-8:]), Leadlogs.user == user, Leadlogs.status == 'Assigned')).first()
    if query:
        query.status = 'Follow up'
        query.updated_date = datetime.now()+timedelta(hours=4)
        session.commit()
        session.close()
    else:
        session.close()

def log_call_center(user, client_name, client_number, status, source, details):
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    newlog = Leadlogs(user=user, client_name=client_name, client_number=client_number, type='Lead', status=status, details=details, source=source, created_date = datetime.now()+timedelta(hours=4))
    session.add(newlog)
    session.commit()
    session.refresh(newlog)
    newlog.refno = 'LOG-L-'+str(newlog.id)
    session.commit()
    session.close()

def edit_lead_callback(user, client_number, source):
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    query = session.query(Leadlogs).filter(and_(Leadlogs.client_number.endswith(client_number[-8:]), Leadlogs.user == user, Leadlogs.status == 'Assigned')).first()
    if query:
        query.status = 'Lead Lost'
        query.source = 'No Action'
        query.details += ' Lead lost of source: '+source
        query.updated_date = datetime.now()+timedelta(hours=4)
        session.commit()
        session.close()
    else:
        session.close()

# logs drafts

@handlelogs.route('/logs/agents/<branch>',methods = ['GET','POST'])
@login_required
def display_all_drafts(branch):   
    if current_user.is_admin == False:
        return abort(404)
    data = []
    f = open('agentlogs_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    if branch == 'ad':
        all_sale_users = db.session.query(User).filter(and_(User.sale == True, User.abudhabi == True)).all()
    elif branch == 'dxb':
        all_sale_users = db.session.query(User).filter(and_(User.sale == True, User.dubai == True)).all()
    else:
        return abort(404)
    return render_template('agents_logs.html', data = data , columns = columns, all_sale_users = all_sale_users, branch = branch)

@handlelogs.route('/fetch_logs/<branch>',methods = ['GET','POST'])
@auth.login_required
def fetch_drafts(branch):
    if branch == 'ad':
        agent_logs = Agentlogs
    elif branch == 'dxb':
        agent_logs = Agentlogsdxb
    search = request.args.get('search')
    offset = int(request.args.get('offset'))
    limit = int(request.args.get('limit'))
    total_records = 0
    data = []
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    query = session.query(agent_logs)
    if search:
        conditions = [column.ilike(f"%{search}%") for column in agent_logs.__table__.columns]
        query = query.filter(or_(*conditions))
    
    if request.args.get('filter') == 'ON':
        conditions = []
        filters_01 = {key: request.args.get(key) for key in request.args}
        filters = {key: filters_01[key] for key in ['user', 'type', 'status', 'propdate', 'propdate2'] if key in filters_01}
        for key, value in filters.items():
            if key == 'propdate':
                conditions.append(agent_logs.created_date >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(agent_logs.created_date <= value)
            else:
                conditions.append(getattr(agent_logs, key) == value)
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
    for r in query.order_by(agent_logs.id.desc()).offset(offset).limit(limit):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        new['created_date'] = new['created_date'][:16]
        new['updated_date'] = new['updated_date'][:16]
        data.append(new)
        total_records += 1
    response_data = {"total": z, "totalNotFiltered": z, "rows": data, "interested_clients": interested_clients, "no_answer": no_answer, "lead_lost": lead_lost}
    session.close()
    return(response_data)

# logs leads

@handlelogs.route('/logs/leads',methods = ['GET','POST'])
@login_required
def display_leads_logs():   
    if current_user.is_admin == False:
        return abort(404)
    data = []
    f = open('agentlogs_headers.json')
    columns = json.load(f)
    columns = columns["lead_headers"]
    all_sale_users = db.session.query(User).filter(and_(User.sale == True, User.abudhabi == True)).all()
    return render_template('leads_logs.html', data = data , columns = columns, all_sale_users = all_sale_users)

@handlelogs.route('/fetch_leads_logs',methods = ['GET','POST'])
@auth.login_required
def fetch_leads_logs():
    search = request.args.get('search')
    offset = int(request.args.get('offset'))
    limit = int(request.args.get('limit'))
    total_records = 0
    data = []
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    query = session.query(Leadlogs)
    if search:
        conditions = [column.ilike(f"%{search}%") for column in Leadlogs.__table__.columns]
        query = query.filter(or_(*conditions))
    
    if request.args.get('filter') == 'ON':
        conditions = []
        filters_01 = {key: request.args.get(key) for key in request.args}
        filters = {key: filters_01[key] for key in ['user', 'source', 'status', 'propdate', 'propdate2'] if key in filters_01}
        for key, value in filters.items():
            if key == 'propdate':
                conditions.append(Leadlogs.created_date >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(Leadlogs.created_date <= value)
            else:
                conditions.append(getattr(Leadlogs, key) == value)
        query = query.filter(and_(*conditions))
    
    z = query.count()
    assigned_leads = 0
    no_action = 0
    lead_lost = 0
    for r in query:
        if r.status == 'Assigned':
            assigned_leads += 1
        elif r.status == 'Lead Lost':
            lead_lost += 1
        else:
            pass
    for r in query.order_by(Leadlogs.id.desc()).offset(offset).limit(limit):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        new['created_date'] = new['created_date'][:16]
        new['updated_date'] = new['updated_date'][:16]
        new['edit'] = '<button class="btn-secondary si2" style="color:white; height: 10px" data-toggle="modal" data-target="#deleteModal" onclick="delete_initiate_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
        data.append(new)
        total_records += 1
    response_data = {"total": z, "totalNotFiltered": z, "rows": data, "assigned_leads": assigned_leads, "lead_lost": lead_lost}
    session.close()
    return(response_data)

# delete lead logs

@handlelogs.route('/delete_leads_logs/<variable>', methods = ['GET','POST'])
@login_required
def delete_lead_log(variable):
    if current_user.is_admin == False:
        return abort(404)
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    delete = session.query(Leadlogs).filter_by(refno=variable).first()
    session.delete(delete)
    session.commit()
    session.close()
    return(jsonify('ok'))

# Logs for Dubai Leads

def lead_update_dubai_log(user, client_name, client_number, status, source, details):
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    newlog = Leadslogsdubai(user=user, client_name=client_name, client_number=client_number, type='Lead', status=status, details=details, source=source, created_date = datetime.now()+timedelta(hours=4))
    session.add(newlog)
    session.commit()
    session.refresh(newlog)
    newlog.refno = 'LOG-LD-'+str(newlog.id)
    session.commit()
    session.close()


@handlelogs.route('/logs/leads-dubai',methods = ['GET','POST'])
@login_required
def display_leads_logsdubai():   
    if current_user.is_admin == False:
        return abort(404)
    data = []
    f = open('agentlogs_headers.json')
    columns = json.load(f)
    columns = columns["lead_headers"]
    all_sale_users = db.session.query(User).filter(and_(User.sale == True, User.dubai == True)).all()
    return render_template('leads_logsdubai.html', data = data , columns = columns, all_sale_users = all_sale_users)


@handlelogs.route('/fetch_leads_logsdubai',methods = ['GET','POST'])
@auth.login_required
def fetch_leads_logsdubai():
    search = request.args.get('search')
    offset = int(request.args.get('offset'))
    limit = int(request.args.get('limit'))
    total_records = 0
    data = []
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    query = session.query(Leadslogsdubai)
    if search:
        conditions = [column.ilike(f"%{search}%") for column in Leadlogs.__table__.columns]
        query = query.filter(or_(*conditions))
    
    if request.args.get('filter') == 'ON':
        conditions = []
        filters_01 = {key: request.args.get(key) for key in request.args}
        filters = {key: filters_01[key] for key in ['user', 'source', 'status', 'propdate', 'propdate2'] if key in filters_01}
        for key, value in filters.items():
            if key == 'propdate':
                conditions.append(Leadslogsdubai.created_date >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(Leadslogsdubai.created_date <= value)
            else:
                conditions.append(getattr(Leadslogsdubai, key) == value)
        query = query.filter(and_(*conditions))
    
    z = query.count()
    assigned_leads = 0
    no_action = 0
    lead_lost = 0
    for r in query:
        if r.status == 'Assigned':
            assigned_leads += 1
        elif r.status == 'Lead Lost':
            lead_lost += 1
        else:
            pass
    for r in query.order_by(Leadslogsdubai.id.desc()).offset(offset).limit(limit):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        new['created_date'] = new['created_date'][:16]
        new['updated_date'] = new['updated_date'][:16]
        new['edit'] = '<button class="btn-secondary si2" style="color:white; height: 10px" data-toggle="modal" data-target="#deleteModal" onclick="delete_initiate_leaddxb_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
        data.append(new)
        total_records += 1
    response_data = {"total": z, "totalNotFiltered": z, "rows": data, "assigned_leads": assigned_leads, "lead_lost": lead_lost}
    session.close()
    return(response_data)



def edit_lead_agent_dubai(user, client_number):
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    query = session.query(Leadslogsdubai).filter(and_(Leadslogsdubai.client_number.endswith(client_number[-8:]), Leadslogsdubai.user == user, Leadslogsdubai.status == 'Assigned')).first()
    if query:
        query.status = 'Follow up'
        query.updated_date = datetime.now()+timedelta(hours=4)
        session.commit()
        session.close()
    else:
        session.close()

# delete dubai lead logs

@handlelogs.route('/delete_leadsdxb_logs/<variable>', methods = ['GET','POST'])
@login_required
def delete_leaddxb_log(variable):
    if current_user.is_admin == False:
        return abort(404)
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    delete = session.query(Leadslogsdubai).filter_by(refno=variable).first()
    session.delete(delete)
    session.commit()
    session.close()
    return(jsonify('ok'))