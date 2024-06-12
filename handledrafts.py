from curses.ascii import NUL
from operator import methodcaller
from xml.dom.minicompat import EmptyNodeList
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import except_all
from models import Leads, Maindraft, User, Activedraft, Maindraftdxb, Activedraftdxb, Leadsdubai
from forms import Draftsusers
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import date, datetime,time
from functions import assign_lead, logs, notes, update_note,lead_email, etisy_message, update_lead_note
from handlelogs import assign_new_draft, edit_draft_agent
from sqlalchemy import or_,and_, bindparam
import csv
from datetime import datetime, timedelta
from flask_httpauth import HTTPTokenAuth
from sqlalchemy.orm import sessionmaker

FILE_UPLOADS = os.getcwd() + "/static/imports/uploads"

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
    
auth = HTTPTokenAuth(scheme='Bearer')
tokens = {
    ''
}

db = SQLAlchemy()

handledrafts = Blueprint('handledrafts', __name__, template_folder='templates')

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return token
    
@handledrafts.route('/fetch_drafts_token',methods = ['GET','POST'])
@login_required
def fetch_drafts_token():
    return(jsonify(''))

# DRAFTS ADMIN

@handledrafts.route('/drafts/admin/<branch>',methods = ['GET','POST'])
@login_required
def display_all_drafts(branch):   
    if current_user.is_admin == False:
        return abort(404)
    data = []
    f = open('draft_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('drafts_admin.html', data = data , columns = columns, branch = branch)

@handledrafts.route('/fetch_drafts/<branch>',methods = ['GET','POST'])
@auth.login_required
def fetch_drafts(branch):
    if branch == 'ad':
        main_draft = Maindraft
        binding = 'second'
    else:
        main_draft = Maindraftdxb
        binding = 'fifth'
    search = request.args.get('search')
    offset = int(request.args.get('offset'))
    limit = int(request.args.get('limit'))
    total_records = 0
    data = []
    
    Session = sessionmaker(bind=db.get_engine(bind=binding))
    session = Session()
    query = session.query(main_draft)
    if search:
        conditions = [column.ilike(f"%{search}%") for column in main_draft.__table__.columns]
        query = query.filter(or_(*conditions))
    
    if request.args.get('filter') == 'ON':
        conditions = []
        filters_01 = {key: request.args.get(key) for key in request.args}
        filters = {key: filters_01[key] for key in ['draft_status', 'status', 'location', 'community', 'type', 'role', 'draft_location', 'draft_community', 'draft_type', 'propdate', 'propdate2', 'source'] if key in filters_01}
        for key, value in filters.items():
            if key == 'propdate':
                conditions.append(main_draft.created_date >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(main_draft.created_date <= value)
            else:
                conditions.append(getattr(main_draft, key) == value)
        query = query.filter(and_(*conditions))
    
    z = query.count()
    for r in query.order_by(main_draft.id.desc()).offset(offset).limit(limit):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        edit_btn =  '<div style="display:flex;"><button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button></div>'
        new["edit"] = edit_btn
        data.append(new)
        total_records += 1
    response_data = {"total": z, "totalNotFiltered": z, "rows": data}
    session.close()
    return(response_data)

@handledrafts.route('/activation_initiated/<branch>',methods = ['GET','POST'])
@login_required
def activation_initiated(branch):   
    if current_user.is_admin == False:
        return abort(404)
    if branch == 'ad':
        main_draft = Maindraft
        binding = 'second'
    else:
        main_draft = Maindraftdxb
        binding = 'fifth'
    filters = request.json
    Session = sessionmaker(bind=db.get_engine(bind=binding))
    session = Session()
    query = session.query(main_draft)
    conditions = []
    valid_filter_keys = ['draft_status', 'status', 'location', 'community', 'type', 'role', 'draft_location', 'draft_community', 'draft_type', 'source' , 'propdate', 'propdate2']
    filtered_filters = {key: filters[key] for key in filters if key in valid_filter_keys}
    for key, value in filtered_filters.items():
            if key == 'propdate':
                conditions.append(main_draft.created_date >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(main_draft.created_date <= value)
            else:
                conditions.append(getattr(main_draft, key) == value)
    query = query.filter(and_(*conditions))
    z = query.count()
    response_data = {key: filtered_filters[key] for key in valid_filter_keys if key in filtered_filters}
    response_data['Total'] = z
    response_json = json.dumps(response_data, indent=4, sort_keys=False)
    session.close()
    return response_json, 200, {'Content-Type': 'application/json'}

@handledrafts.route('/activation_execute/<branch>',methods = ['GET','POST'])
@login_required
def activation_execute(branch):   
    if current_user.is_admin == False:
        return abort(404)
    if branch == 'ad':
        main_draft = Maindraft
        active_drafts = Activedraft
        binding = 'second'
    else:
        main_draft = Maindraftdxb
        active_drafts = Activedraftdxb
        binding = 'fifth'
    filters = request.json
    Session = sessionmaker(bind=db.get_engine(bind=binding))
    session = Session()
    maindrafts_query = session.query(main_draft)
    conditions = []
    valid_filter_keys = ['draft_status', 'status', 'location', 'community', 'type','role', 'draft_location', 'draft_community', 'draft_type', 'source', 'propdate', 'propdate2']
    filtered_filters = {key: filters[key] for key in filters if key in valid_filter_keys}
    for key, value in filtered_filters.items():
            if key == 'propdate':
                conditions.append(main_draft.created_date >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(main_draft.created_date <= value)
            else:
                conditions.append(getattr(main_draft, key) == value)
    maindrafts_query = maindrafts_query.filter(and_(*conditions))

    counter = 0
    for maindraft in maindrafts_query:
        activedraft = active_drafts(refno=maindraft.refno, name=maindraft.name, number=maindraft.number, role=maindraft.role, location=maindraft.location, community=maindraft.community, type=maindraft.type, status='Pending', source=maindraft.source, lead_refno=maindraft.lead_refno, activated_date=datetime.now()+timedelta(hours=4), updated_date=datetime.now()+timedelta(hours=4))
        session.add(activedraft)
        maindraft.draft_status = 'Active'
        counter += 1
        if counter >= int(filters['activation_number']):
            break
    
    session.commit()
    session.close()
    response_data = 'Draft Activation successfuly completed.'
    response_json = json.dumps(response_data, indent=4, sort_keys=False)
    return response_json, 200, {'Content-Type': 'application/json'}


# Uploading Data Abu Dhabi

@handledrafts.route('/upload_drafts',methods = ['GET','POST'])
@login_required
def upload_drafts():
    uploaded_file = request.files['file']
    filepath = os.path.join(FILE_UPLOADS, uploaded_file.filename)
    uploaded_file.save(filepath)
    results = {}
    Session = sessionmaker(bind=db.get_engine(bind='second'))
    session = Session()
    query = session.query(Maindraft)
    Session_second = sessionmaker(bind=db.get_engine(bind='primary'))
    session_leads = Session_second()
    query_leads = session_leads.query(Leads)
    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print("Lesssgooo with count = 0")
                line_count += 1
                results['Started'] = 'Positive'
            elif row[0] != '' and row[0] != 'contact_name':
                try:
                    num_check = row[1].replace(" ", "").replace("+","")[3:]
                    i = query.filter(Maindraft.number.endswith(num_check)).first()
                    if (i):
                        results[row[0]] = 'DUPLICATE'
                    else: 
                        i = query_leads.filter(Leads.contact_number.endswith(num_check)).first()
                        if (i):
                            source = 'Lead'
                            lead_refno = i.refno
                            created_date = i.created_date
                            last_updated = datetime.now()+timedelta(hours=4)
                        else:
                            source = 'Raw'
                            lead_refno = '-'
                            created_date = datetime.now()+timedelta(hours=4)
                            last_updated = datetime.now()+timedelta(hours=4)
                        name = row[0]
                        number = row[1].replace(" ", "").replace("+","")
                        role = row[2]
                        location = row[3]
                        community = row[4]
                        type = row[5]
                        status = 'Pending'
                        draft_status = 'In-Active'
                        draft_location = '-'
                        draft_community = '-'
                        draft_type = '-'
                        newdraft = Maindraft(name=name, number=number, role=role, location=location, community=community, type=type, status=status, draft_status=draft_status, draft_location=draft_location, draft_community=draft_community, draft_type=draft_type, created_date=created_date, last_updated=last_updated, source=source, lead_refno=lead_refno)
                        session.add(newdraft)
                        session.commit()
                        session.refresh(newdraft)
                        newdraft.refno = 'UNI-RD-'+str(newdraft.id)
                        session.commit()
                except Exception as e:
                    error_message = str(e)  # Get the error message
                    results[row[0]] = f'Error adding this Lead: {error_message}'
                line_count += 1
                print(line_count)
            else:
                break
        print(f'Processed {line_count} lines.')
        results['Draft Batch'] = 'Completely Processed'
        response_data = json.dumps(results, default=lambda x: str(x), indent=2)
        session.close()
        session_leads.close()
    return response_data, 200, {'Content-Type': 'application/json'}

# DRAFTS QA / CALL CENTER

@handledrafts.route('/drafts/call-center/<branch>',methods = ['GET','POST'])
@login_required
def display_active_drafts(branch):   
    if current_user.is_admin == False:
        return abort(404)
    data = []
    f = open('draft_headers.json')
    columns = json.load(f)
    columns = columns["headers_call_center"]
    if branch == 'ad':
        all_sale_users = db.session.query(User).filter(and_(User.sale == True, User.abudhabi == True)).all()
    elif branch == 'dxb':
        all_sale_users = db.session.query(User).filter(and_(User.sale == True, User.dubai == True)).all()
    else:
        return abort(404)
    return render_template('drafts_qa.html', data = data , columns = columns, all_sale_users = all_sale_users, branch = branch)

@handledrafts.route('/fetch_active_drafts/<branch>',methods = ['GET','POST'])
@auth.login_required
def fetch_active_drafts(branch):
    if branch == 'ad':
        active_drafts = Activedraft
        binding = 'second'
    else:
        active_drafts = Activedraftdxb
        binding = 'fifth'
    search = request.args.get('search')
    offset = int(request.args.get('offset'))
    limit = int(request.args.get('limit'))
    total_records = 0
    data = []
    
    Session = sessionmaker(bind=db.get_engine(bind=binding))
    session = Session()
    query = session.query(active_drafts)
    if search:
        conditions = [column.ilike(f"%{search}%") for column in active_drafts.__table__.columns]
        query = query.filter(or_(*conditions))
    
    if request.args.get('filter') == 'ON':
        conditions = []
        filters_01 = {key: request.args.get(key) for key in request.args}
        filters = {key: filters_01[key] for key in ['status', 'location', 'community', 'type','role', 'propdate', 'propdate2', 'source'] if key in filters_01}
        for key, value in filters.items():
            if key == 'propdate':
                conditions.append(active_drafts.updated_date >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(active_drafts.updated_date <= value)
            else:
                conditions.append(getattr(active_drafts, key) == value)
        query = query.filter(and_(*conditions))
    
    z = query.count()
    for r in query.order_by(active_drafts.id.desc()).offset(offset).limit(limit):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        options_button = '<div style="display:flex;"><button style="padding: 3px 5px 3px 5px !important;" class="btn btn-primary" onclick="draft_action_('"'"+'new_lead'+"',"+"'"+new['refno']+"'"+')"><i style="font-size: 1.5em;" class="bi bi-plus-square"></i></button>'
        options_button1 = '<button style="padding: 3px 5px 3px 5px !important;" class="btn btn-primary" onclick="draft_action_('"'"+'reassign'+"',"+"'"+new['refno']+"'"+')"><i style="font-size: 1.5em;" class="bi bi-arrow-repeat"></i></button>'
        options_button2 = '<button style="padding: 3px 5px 3px 5px !important;" class="btn btn-primary" onclick="draft_action_('"'"+'no_action'+"',"+"'"+new['refno']+"'"+')"><i style="font-size: 1.5em;" class="bi bi-x-circle-fill"></i></button></div>'
        new["edit"] = options_button+options_button1+options_button2
        data.append(new)
        total_records += 1
    response_data = {"total": z, "totalNotFiltered": z, "rows": data}
    session.close()
    return(response_data)

@handledrafts.route('/assignment_initiated/<branch>',methods = ['GET','POST'])
@login_required
def assignment_initiated(branch):   
    if current_user.is_admin == False:
        return abort(404)
    if branch == 'ad':
        active_drafts = Activedraft
        binding = 'second'
    elif branch == 'dxb':
        active_drafts = Activedraftdxb
        binding = 'fifth'
    else:
        return abort(404)
    filters = request.json
    Session = sessionmaker(bind=db.get_engine(bind=binding))
    session = Session()
    query = session.query(active_drafts)
    conditions = []
    valid_filter_keys = ['status', 'location', 'community', 'type', 'role', 'source' , 'propdate', 'propdate2']
    filtered_filters = {key: filters[key] for key in filters if key in valid_filter_keys}
    for key, value in filtered_filters.items():
            if key == 'propdate':
                conditions.append(active_drafts.updated_date >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(active_drafts.updated_date <= value)
            else:
                conditions.append(getattr(active_drafts, key) == value)
    query = query.filter(and_(*conditions))
    z = query.count()
    response_data = {key: filtered_filters[key] for key in valid_filter_keys if key in filtered_filters}
    response_data['Total'] = z
    response_json = json.dumps(response_data, indent=4, sort_keys=False)
    session.close()
    return response_json, 200, {'Content-Type': 'application/json'}

@handledrafts.route('/assignment_execute/<branch>',methods = ['GET','POST'])
@login_required
def assignment_execute(branch):   
    if current_user.is_admin == False:
        return abort(404)
    if branch == 'ad':
        active_drafts = Activedraft
        binding = 'second'
    elif branch == 'dxb':
        active_drafts = Activedraftdxb
        binding = 'fifth'
    else:
        return abort(404)
    filters = request.json
    Session = sessionmaker(bind=db.get_engine(bind=binding))
    session = Session()
    activedrafts_query = session.query(active_drafts)
    conditions = []
    valid_filter_keys = ['status', 'location', 'community', 'type', 'role', 'draft_location', 'draft_community', 'draft_type', 'source', 'propdate', 'propdate2']
    filtered_filters = {key: filters[key] for key in filters if key in valid_filter_keys}
    for key, value in filtered_filters.items():
            if key == 'propdate':
                conditions.append(active_drafts.updated_date >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(active_drafts.updated_date <= value)
            else:
                conditions.append(getattr(active_drafts, key) == value)
    activedrafts_query = activedrafts_query.filter(and_(*conditions))

    counter = 0
    for activedraft in activedrafts_query:
        activedraft.assign_to = filters['assignment_user']
        activedraft.status = 'Assigned'
        activedraft.updated_date = datetime.now()+timedelta(hours=4)
        try:
            x = assign_new_draft(filters['assignment_user'], activedraft.name, activedraft.number, branch)
        except:
            pass
        counter += 1
        if counter >= int(filters['assignment_number']):
            break
    
    session.commit()
    session.close()
    response_data = 'Draft Activation successfuly completed.'
    response_json = json.dumps(response_data, indent=4, sort_keys=False)
    return response_json, 200, {'Content-Type': 'application/json'}

@handledrafts.route('/new_draft_lead/<branch>',methods = ['GET','POST'])
@login_required
def draft_action(branch):  
    if branch == 'ad':
        main_draft = Maindraft
        active_drafts = Activedraft
        binding = 'second'
    elif branch == 'dxb':
        main_draft = Maindraftdxb
        active_drafts = Activedraftdxb
        binding = 'fifth'
    else:
        return abort(404)
    actions = request.json
    Session = sessionmaker(bind=db.get_engine(bind=binding))
    session = Session()
    active_query = session.query(active_drafts).filter_by(refno = actions['refno']).first()
    main_query = session.query(main_draft).filter_by(refno = actions['refno']).first()
    main_query.draft_status = 'In-Active'
    if actions['task'] == 'no_action':
        main_query.status = active_query.status
        main_query.draft_location = active_query.update_location
        main_query.draft_community = active_query.update_community
        main_query.draft_type = active_query.update_type
        main_query.last_updated = datetime.now()+timedelta(hours=4)
    elif actions['task'] == 'new_lead':
        main_query.draft_location = active_query.update_location
        main_query.draft_community = active_query.update_community
        main_query.draft_type = active_query.update_type
        main_query.status = active_query.status
        main_query.last_updated = datetime.now()+timedelta(hours=4)
        main_query.source = 'Lead'
        relink = relink_lead_draft(active_query.number, branch)
        main_query.lead_refno = relink['lead_refno']
        main_query.created_date = relink['created_date']
    elif actions['task'] == 'reassign':
        main_query.draft_location = active_query.update_location
        main_query.draft_community = active_query.update_community
        main_query.draft_type = active_query.update_type
        main_query.status = active_query.status
        main_query.last_updated = datetime.now()+timedelta(hours=4)
        relink = relink_lead_draft(active_query.number, branch)
        main_query.lead_refno = relink['lead_refno']
        main_query.created_date = relink['created_date']
    else:
        pass
    session.delete(active_query)
    session.commit()
    session.close()
    return jsonify('ok')

def relink_lead_draft(number, branch):
    if branch == 'ad':
        leads_db = Leads
        binding = 'primary'
    elif branch == 'dxb':
        leads_db = Leadsdubai
        binding = 'fourth'
    else:
        return abort(404)
    Session_second = sessionmaker(bind=db.get_engine(bind=binding))
    session_leads = Session_second()
    query_leads = session_leads.query(leads_db)
    i = query_leads.filter(leads_db.contact_number.endswith(number[-8:])).first()
    relink = {}
    if (i):
        relink['lead_refno'] = i.refno
        relink['created_date'] = i.created_date
        return(relink)
    else:
        return abort(404)


# DRAFTS AGENTS

@handledrafts.route('/drafts/agent/<branch>', methods = ['GET','POST'])
@login_required
def drafts_agent(branch):
    if current_user.sale == False:
        return abort(404) 
    if branch == 'ad':
        active_drafts = Activedraft
        binding = 'second'
    elif branch == 'dxb':
        active_drafts = Activedraftdxb
        binding = 'fifth'
    else:
        return abort(404)
    Session = sessionmaker(bind=db.get_engine(bind=binding))
    session = Session()
    edit = session.query(active_drafts).filter_by(assign_to=current_user.username, status='Assigned').first()
    if edit is None:
        session.close()
        return 'You do not have any active drafts' 
    template = "drafts_agent.html"
    form = Draftsusers(obj = edit)
    w = open('abudhabi.json')
    mydict = json.load(w)
    new = form.update_location.data
    try:
        form.update_location.data = list(mydict.keys())[list(mydict.values()).index(edit.update_location)]
    except:
        form.update_location.data = ""
    if request.method == 'POST':
        edit.updated_date = datetime.now()+timedelta(hours=4)
        form.populate_obj(edit)
        try:
            edit.update_location = mydict[new]
        except:
            edit.update_location = ""

        try:
            if edit.comment == "":
                edit.comment = '-'
            x = edit_draft_agent(edit.assign_to, edit.number, edit.status, edit.comment, branch)
        except:
            pass

        if edit.status == 'Call Later' or edit.status == 'No Answer' or edit.status == 'Do Not Call' or edit.status == 'Not Interested':
            actions = {
                'refno': edit.refno,
                'status': edit.status
                }
            justdoit = draft_action_user(actions, branch)
        else:
            session.commit()

        session.close()
        return redirect(url_for('handledrafts.drafts_agent', branch = branch))
    session.close()
    return render_template(template, form=form, update_community = edit.update_community)

def draft_action_user(actions, branch):
    if current_user.sale == False:
        return abort(404) 
    if branch == 'ad':
        main_draft = Maindraft
        active_drafts = Activedraft
        binding = 'second'
    elif branch == 'dxb':
        main_draft = Maindraftdxb
        active_drafts = Activedraftdxb
        binding = 'fifth'
    else:
        return abort(404)
    Session = sessionmaker(bind=db.get_engine(bind=binding))
    session = Session()
    active_query = session.query(active_drafts).filter_by(refno = actions['refno']).first()
    main_query = session.query(main_draft).filter_by(refno = actions['refno']).first()
    main_query.draft_status = 'In-Active'
    main_query.status = actions['status']
    main_query.last_updated = datetime.now()+timedelta(hours=4)
    session.delete(active_query)
    session.commit()
    session.close()
    return jsonify('ok')

@handledrafts.route('/delete_draft/<branch>/<variable>', methods = ['GET','POST'])
@login_required
def delete_draft(branch, variable):
    if current_user.is_admin == False:
        return abort(404)
    if branch == 'ad':
        main_draft = Maindraft
        binding = 'second'
    elif branch == 'dxb':
        main_draft = Maindraftdxb
        binding = 'fifth'
    else:
        return abort(404)
    Session = sessionmaker(bind=db.get_engine(bind=binding))
    session = Session()
    delete = session.query(main_draft).filter_by(refno=variable).first()
    session.delete(delete)
    session.commit()
    session.close()
    return redirect(url_for('handledrafts.display_all_drafts', branch = branch))

# Uploading Data Abu Dhabi

@handledrafts.route('/upload_drafts_dxb',methods = ['GET','POST'])
@login_required
def upload_drafts_dxb():
    uploaded_file = request.files['file']
    filepath = os.path.join(FILE_UPLOADS, uploaded_file.filename)
    uploaded_file.save(filepath)
    results = {}
    Session = sessionmaker(bind=db.get_engine(bind='fifth'))
    session = Session()
    query = session.query(Maindraftdxb)
    Session_second = sessionmaker(bind=db.get_engine(bind='fourth'))
    session_leads = Session_second()
    query_leads = session_leads.query(Leadsdubai)
    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print("Lesssgooo with count = 0")
                line_count += 1
                results['Started'] = 'Positive'
            elif row[0] != '' and row[0] != 'contact_name':
                try:
                    num_check = row[1].replace(" ", "").replace("+","")[3:]
                    i = query.filter(Maindraftdxb.number.endswith(num_check)).first()
                    if (i):
                        results[row[0]] = 'DUPLICATE'
                    else: 
                        i = query_leads.filter(Leadsdubai.contact_number.endswith(num_check)).first()
                        if (i):
                            source = 'Lead'
                            lead_refno = i.refno
                            created_date = i.created_date
                            last_updated = datetime.now()+timedelta(hours=4)
                        else:
                            source = 'Raw'
                            lead_refno = '-'
                            created_date = datetime.now()+timedelta(hours=4)
                            last_updated = datetime.now()+timedelta(hours=4)
                        name = row[0]
                        number = row[1].replace(" ", "").replace("+","")
                        role = row[2]
                        location = row[3]
                        community = row[4]
                        type = row[5]
                        status = 'Pending'
                        draft_status = 'In-Active'
                        draft_location = '-'
                        draft_community = '-'
                        draft_type = '-'
                        newdraft = Maindraftdxb(name=name, number=number, role=role, location=location, community=community, type=type, status=status, draft_status=draft_status, draft_location=draft_location, draft_community=draft_community, draft_type=draft_type, created_date=created_date, last_updated=last_updated, source=source, lead_refno=lead_refno)
                        session.add(newdraft)
                        session.commit()
                        session.refresh(newdraft)
                        newdraft.refno = 'UNI-RD-'+str(newdraft.id)
                        session.commit()
                except Exception as e:
                    error_message = str(e)  # Get the error message
                    results[row[0]] = f'Error adding this Lead: {error_message}'
                line_count += 1
                print(line_count)
            else:
                break
        print(f'Processed {line_count} lines.')
        results['Draft Batch'] = 'Completely Processed'
        response_data = json.dumps(results, default=lambda x: str(x), indent=2)
        session.close()
        session_leads.close()
    return response_data, 200, {'Content-Type': 'application/json'}