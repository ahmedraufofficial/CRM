from curses.ascii import NUL
from operator import methodcaller
from xml.dom.minicompat import EmptyNodeList
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import except_all
from models import Leads, Contacts, User, Leadsdubai, Contactsdubai
from forms import AddLeadForm, BuyerLead, BuyerLeadDubai
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import date, datetime,time
from functions import assign_lead, logs, etisy_message, update_user_note
from sqlalchemy import or_,and_
import csv
from datetime import datetime, timedelta
from flask_httpauth import HTTPTokenAuth
from handlelogs import lead_update_dubai_log, edit_lead_agent_dubai
from sqlalchemy.orm import sessionmaker

auth = HTTPTokenAuth(scheme='Bearer')
tokens = {
    ''
}

NOTES = os.getcwd() + '/static2/notes'
FILE_UPLOADS = os.getcwd() + "/static/imports/uploads"

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

db = SQLAlchemy()

handleleadsdxb = Blueprint('handleleadsdxb', __name__, template_folder='templates')

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return token

@handleleadsdxb.route('/fetch_leadsdxb_token',methods = ['GET','POST'])
@login_required
def fetch_leadsdxb_token():
    return(jsonify(''))

@handleleadsdxb.route('/fetch_leadsdxb/<user>',methods = ['GET','POST'])
@auth.login_required
def fetch_leadsdxb(user):
    voltage_user = db.session.query(User).filter_by(username = user).first()
    search = request.args.get('search')
    offset = int(request.args.get('offset'))
    limit = int(request.args.get('limit'))
    total_records = 0
    data = []
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    query = session.query(Leadsdubai).filter_by(street=0)
    if search:
        conditions = [column.ilike(f"%{search}%") for column in Leadsdubai.__table__.columns]
        query = query.filter(or_(*conditions))
    
    if request.args.get('filter') == 'ON':
        conditions = []
        filters_01 = {key: request.args.get(key) for key in request.args}
        filters = {key: filters_01[key] for key in ['min_beds', 'lead_type', 'subtype', 'locationtext', 'building', 'agent', 'propdate', 'propdate2', 'status', 'source'] if key in filters_01}
        for key, value in filters.items():
            if key == 'propdate':
                conditions.append(Leadsdubai.lastupdated >= value)
            elif key == 'propdate2':
                value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
                value_as_datetime += timedelta(days=1)
                value = value_as_datetime.strftime('%Y-%m-%d')
                conditions.append(Leadsdubai.lastupdated <= value)
            elif key == 'status':
                conditions.append(getattr(Leadsdubai, key) == 'Open')
            else:
                conditions.append(getattr(Leadsdubai, key) == value)
        query = query.filter(and_(*conditions))
    
    if voltage_user.is_admin == True or voltage_user.qa == True:
        z = query.count()
        for r in query.order_by(Leadsdubai.lastupdated.desc()).offset(offset).limit(limit):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            edit_btn =  '<a href="/edit_leaddxb/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a><button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            reassign_straight = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#reassignModal"  onclick="assign_straight_initiate('+"'"+new['refno']+"'"+')"><i class="bi bi-forward-fill"></i></button>' #directly re-assigns
            if new['agent'] == voltage_user.username and new['sub_status'] == "In progress":
                followupBG = 'background-color:rgba(19, 132, 150,0.7);border-radius:20px;box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-webkit-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-moz-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);'
            else:
                followupBG = ""
            new["edit"] = "<div style='display:flex;"+followupBG+"'>"+edit_btn +'<button class="btn-danger si2" data-toggle="modal" data-target="#viewModal"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-arrows-fullscreen"></i></button>'+'<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+reassign_straight+"</div>"
            data.append(new)
            total_records += 1
        response_data = {"total": z, "totalNotFiltered": z, "rows": data}
        session.close()
        return(response_data)
    elif voltage_user.team_lead == True:
        query_team = query.filter(or_(Leadsdubai.created_by == voltage_user.username,Leadsdubai.agent == voltage_user.username))
        for i in voltage_user.team_members.split(','):
            query2 = query.filter(or_(Leadsdubai.created_by == i,Leadsdubai.agent == i))
            query_team = query_team.union(query2)
        z = query_team.count()
        for r in query_team.order_by(Leadsdubai.lastupdated.desc()).offset(offset).limit(limit):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            if voltage_user.edit == True:
                edit_btn =  '<a href="/edit_lead/'+str(new['type'])+'/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a><button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            else:
                edit_btn = ''
            if new['agent'] == voltage_user.username and new['sub_status'] == "In progress":
                followupBG = 'background-color:rgba(19, 132, 150,0.7);border-radius:20px;box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-webkit-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-moz-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);'
            else:
                followupBG = ""
            new["edit"] = "<div style='display:flex;"+followupBG+"'>"+edit_btn +'<button class="btn-danger si2" data-toggle="modal" data-target="#viewModal"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-arrows-fullscreen"></i></button>'+'<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+"</div>"
            data.append(new)
            total_records += 1
        response_data = {"total": z, "totalNotFiltered": z, "rows": data}
        session.close()
        return(response_data)
    else:
        query = query.filter(Leadsdubai.agent == voltage_user.username)
        z = query.count()
        for r in query.order_by(Leadsdubai.lastupdated.desc()).offset(offset).limit(limit):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            new['created_date'] = '-'
            new['source'] = '-'
            if voltage_user.edit == True:
                if r.created_by == voltage_user.username or r.agent == voltage_user.username:
                    edit_btn =  '<a href="/edit_lead/'+str(new['type'])+'/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a><button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
                else:
                    edit_btn = ''
            else:
                edit_btn = ''
            if new['agent'] == voltage_user.username and new['sub_status'] == "In progress":
                followupBG = 'background-color:#138496;background-color:rgba(19, 132, 150,0.7);border-radius:20px;'
            else:
                followupBG = ""
            new["edit"] = "<div style='display:flex; "+followupBG+"'>"+edit_btn +'<button class="btn-danger si2" data-toggle="modal" data-target="#viewModal"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-arrows-fullscreen"></i></button>'+'<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+"</div>"
            data.append(new)
        response_data = {"total": z, "totalNotFiltered": z, "rows": data}
        session.close()
        return(response_data)
    
@handleleadsdxb.route('/leadsdxb',methods = ['GET','POST'])
@login_required
def display_leadsdxb():   
    if current_user.sale == False or current_user.dubai == False:
        return abort(404)
    data = []
    f = open('lead_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    all_sale_users = db.session.query(User).filter(and_(User.sale == True, User.dubai == True)).all()
    return render_template('leadsdxb.html', data = data , columns = columns, user=current_user.username, all_sale_users = all_sale_users)


@handleleadsdxb.route('/delete_leaddxb/<variable>', methods = ['GET','POST'])
@login_required
def delete_leaddxb(variable):
    if current_user.sale == False or current_user.edit == False or current_user.dubai == False:
        return abort(404) 
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    delete = session.query(Leadsdubai).filter_by(refno=variable).first()
    session.delete(delete)
    session.commit()
    f = NOTES+'/'+str(variable)+'.json'
    try:
        os.remove(f)
    except OSError as error:
        print(error)
        return("Directory '% s' can not be removed but contact removed, Contact your tech support" % f)
    session.close()
    return redirect(url_for('handleleadsdxb.display_leadsdxb'))


@handleleadsdxb.route('/add_leaddxb_buyer/', methods = ['GET','POST'])
@login_required
def add_leaddxb_buyer():
    if current_user.sale == False or current_user.dubai == False:
        return abort(404)  
    form = BuyerLeadDubai()
    if request.method == 'POST':
        Session = sessionmaker(bind=db.get_engine(bind='fourth'))
        session = Session()
        contact = form.contact.data
        contact_name = form.contact_name.data
        contact_number = form.contact_number.data
        contact_email = form.contact_email.data
        nationality = form.nationality.data
        role = form.role.data
        source = form.source.data
        time_to_contact = form.time_to_contact.data
        agent = form.agent.data
        enquiry_date = form.enquiry_date.data
        purpose = form.purpose.data
        propertyamenities =  ",".join(form.propertyamenities.data)
        status = form.status.data
        sub_status = form.sub_status.data
        property_requirements = form.property_requirements.data
        w = open('abudhabi.json')
        file_data = json.load(w)
        try:
            locationtext = file_data[form.locationtext.data]
        except:
            locationtext = "None"
        building = form.building.data
        sendSMS = form.sendSMS.data
        subtype = form.subtype.data
        min_beds = form.min_beds.data
        max_beds = form.max_beds.data
        min_price = form.min_price.data
        max_price = form.max_price.data
        unit = form.unit.data
        plot = form.plot.data
        street = form.street.data
        size = form.size.data
        lead_type = form.lead_type.data
        created_date = datetime.now()+timedelta(hours=4)
        lastupdated = datetime.now()+timedelta(hours=4)
        branch = form.branch.data
        newlead = Leadsdubai(type="secondary",lastupdated=lastupdated,created_date=created_date,role=role,source=source,contact = contact,contact_name = contact_name,contact_number = contact_number,contact_email = contact_email,nationality = nationality,time_to_contact = time_to_contact,agent = agent,enquiry_date = enquiry_date,purpose = purpose,propertyamenities = propertyamenities,created_by=current_user.username,status = status,sub_status = sub_status,property_requirements = property_requirements,locationtext = locationtext,building = building,subtype = subtype,min_beds = min_beds,max_beds = max_beds,min_price = min_price,max_price = max_price,unit = unit,plot = plot,street = street,size = size,lead_type=lead_type, branch=branch)
        session.add(newlead)
        session.commit()
        session.refresh(newlead)
        newlead.refno = 'UNI-LD-'+str(newlead.id)
        session.commit()
        logs(current_user.username,'UNI-LD-'+str(newlead.id),'Added')
        notesdxb('UNI-LD-' + str(newlead.id))
        assign_lead(current_user.username,'UNI-LD-'+str(newlead.id),newlead.sub_status)

        if (sendSMS == "1"):
            if (agent!= "" or agent!= None or contact_name!= "" or contact_name!= None):
                get_agent = db.session.query(User).filter_by(username = agent).first()
                try:
                    etisy_message(agent,contact_name,get_agent.number,contact_number, newlead.refno, locationtext, building, lead_type)
                except:
                    pass
            else:
                pass
        else:
            pass

        message = "Lead assigned to "+agent
        if locationtext != '':
            message += ' in '+locationtext
        else:
            pass
        if building != '':
            message += ', '+building
        else:
            pass
        update_lead_notedxb('Admin', newlead.refno, message, status, sub_status)
        
        session.close()
        return redirect(url_for('handleleadsdxb.display_leadsdxb'))
    return render_template('add_lead_buyer.html', form=form, user = current_user.username, vibes = 'dxb')

@handleleadsdxb.route('/edit_leaddxb/<var>', methods = ['GET','POST'])
@login_required
def edit_leaddxb(var):
    if current_user.sale == False or current_user.edit == False or current_user.dubai == False:
        return abort(404) 
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    edit = session.query(Leadsdubai).filter_by(refno = var).first()
    template = "add_lead_buyer.html" 
    form = BuyerLeadDubai(obj = edit)
    w = open('abudhabi.json')
    mydict = json.load(w)
    new = form.locationtext.data
    try:
        form.locationtext.data = list(mydict.keys())[list(mydict.values()).index(edit.locationtext)]
    except:
        form.locationtext.data = ""
    if request.method == 'POST':
        edit.lastupdated = datetime.now()+timedelta(hours=4)
        form.populate_obj(edit)
        edit.propertyamenities = ",".join(form.propertyamenities.data)
        try:
            edit.locationtext = mydict[new]
        except:
            edit.locationtext = ""
        session.commit()

        if (edit.sendSMS == "1"):
            if (edit.agent!= "" or edit.agent!= None or edit.contact_name!= "" or edit.contact_name!= None):
                get_agent = db.session.query(User).filter_by(username = edit.agent).first()
                try:
                    etisy_message(edit.agent,edit.contact_name,get_agent.number,edit.contact_number, edit.refno, edit.locationtext, edit.building, edit.lead_type)
                except:
                    pass
            else:
                pass
        else:
            pass

        logs(current_user.username,edit.refno,'Edited')
        session.close()
        return redirect(url_for('handleleadsdxb.display_leadsdxb'))
    if edit.propertyamenities  != None:
        form.propertyamenities.data = edit.propertyamenities.split(',')
    session.close()
    return render_template(template, form=form,building = edit.building,assign=edit.agent, user = current_user.username, sub_status = edit.sub_status, vibes = 'dxb')


#@handleleadsdxb.route('/status/<substatus>',methods = ['GET','POST'])
#@login_required
#def community(substatus):
#    a = substatus
#    status = []
#    stats_open = ['In progress','Flag','Not yet contacted','Called no reply','Follow up','Offer made','Viewing arranged','Viewing Done','Interested','Interested to meet','Not interested','Needs time','Client not reachable']
#    stats_closed = ['Successful', 'Unsuccessful']
#    if a == 'Open':
#        for i in stats_open:
#            status.append((i,i))
#    elif a == 'Closed': 
#        for i in stats_closed:
#            status.append((i,i))
#    return jsonify({'status':status})

# Uploading Bulk Leads Module

@handleleadsdxb.route('/upload/leads-bulk')
def upload_leads():
    return render_template('upload_leads.html')

@handleleadsdxb.route('/uploadleadsdubai',methods = ['GET','POST'])
@login_required
def uploadleadsdxb():
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    uploaded_file = request.files['file']
    filepath = os.path.join(FILE_UPLOADS, uploaded_file.filename)
    uploaded_file.save(filepath)
    results = {}
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
                    i = session.query(Contactsdubai).filter(Contactsdubai.number.endswith(num_check)).first()
                    if (i):
                        results[row[0]] = 'DUPLICATE'
                    else: 
                        first_name = row[0].split(" ")[0]
                        if len(row[0].split(" ")) > 1: 
                            last_name = ' '.join(row[0].split(" ")[1:])
                        else: 
                            last_name = ''
                        number = row[1].replace(" ", "").replace("+","")
                        email = row[2]
                        newcontact = Contactsdubai(first_name=first_name, last_name=last_name ,number=number,email=email, assign_to='naira_amin', source = row[10], created_by='naira_amin', branch = 'Dubai')
                        session.add(newcontact)
                        session.commit()
                        session.refresh(newcontact)
                        newcontact.refno = 'UNI-CD-'+str(newcontact.id)
                        session.commit()
                        contact = 'UNI-CD-'+str(newcontact.id)
                        contact_name = row[0]
                        contact_number = row[1].replace(" ", "").replace("+","")
                        contact_email = row[2]
                        role = row[3]
                        #agent = row[4]
                        lead_type = row[5]
                        locationtext = row[6]
                        building = row[7]
                        subtype = row[8]
                        min_beds = row[9]
                        source = row[10]
                        lastupdated = datetime.now()+timedelta(hours=4)
                        created_date = datetime.now()+timedelta(hours=4)
                        newlead = Leadsdubai(type="secondary",lastupdated=lastupdated,created_date=created_date,role=role,source=source,contact = contact,contact_name = contact_name,contact_number = contact_number,contact_email = contact_email,created_by='naira_amin',status = 'Open',sub_status = 'In progress',locationtext = locationtext,building = building,subtype = subtype,min_beds = min_beds,unit = '-',street = '1',lead_type=lead_type, purpose = 'Live in', branch = 'Dubai')
                        session.add(newlead)
                        session.commit()
                        session.refresh(newlead)
                        newlead.refno = 'UNI-LD-'+str(newlead.id)
                        session.commit() 
                        notesdxb('UNI-LD-' + str(newlead.id))
                        assign_lead(current_user.username,'UNI-LD-'+str(newlead.id),newlead.sub_status) 
                        #if (row[11] == "Yes"):
                        #    if (agent!= "" or agent!= None or contact_name!= "" or contact_name!= None):
                        #        get_agent = db.session.query(User).filter_by(username = agent).first()
                        #        try:
                        #            etisy_message(agent,contact_name,get_agent.number,contact_number, newlead.refno, locationtext, building, lead_type)
                        #        except:
                        #            pass
                        #    else:
                        #        pass
                        #else:
                        #    pass
                        #message = "Lead assigned to "+agent
                        #if locationtext != '':
                        #    message += ' in '+locationtext
                        #else:
                        #    pass
                        #if building != '':
                        #    message += ', '+building
                        #else:
                        #    pass
                        #try:
                        #    update_lead_notedxb('Admin', newlead.refno, message, 'Open', 'In progress')
                        #except:
                        #    pass
                        results[row[0]] = 'Successfully Added'
                        #try:
                        #    first_time = lead_update_log(user=agent, client_name=contact_name, client_number=contact_number, status='Assigned', source=source, details='via Bulk-Leads')
                        #except:
                        #    pass
                except:
                    results[row[0]] = 'Error adding this Lead'
                line_count += 1
                print(line_count)
            else:
                break
        print(f'Processed {line_count} lines.')
        results['Batch'] = 'Completely Processed'
        response_data = json.dumps(results, default=lambda x: str(x), indent=2)
        session.close()
    return response_data, 200, {'Content-Type': 'application/json'}

# Directly re assign Leads LESSSGOOO!!! SUIIIIIII

@handleleadsdxb.route('/reassign_leaddxb_straight/<x>/<y>/<z>')
@login_required
def reassign_straight_function_dxb(x, y, z):
    if current_user.sale == False or current_user.edit == False or current_user.dubai == False:
        return abort(404) 
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    edit = session.query(Leadsdubai).filter_by(refno=x).first()
    previous_agent = edit.agent
    edit.agent = y
    edit.sub_status = 'In progress'
    edit.source = z.replace("%20", " ")
    edit.lastupdated = datetime.now()+timedelta(hours=4)
    session.commit()
    if (edit.contact_name!= "" or edit.contact_name!= None):
        get_agent = db.session.query(User).filter_by(username = edit.agent).first()
        try:
            etisy_message(edit.agent,edit.contact_name,get_agent.number,edit.contact_number, edit.refno, edit.locationtext, edit.building, edit.lead_type)
        except:
            pass
    else:
        pass
    message = "Lead re-assigned to "+y
    if edit.locationtext != '':
        message += ' in '+edit.locationtext
    else:
        pass
    if edit.building != '':
        message += ', '+edit.building
    else:
        pass
    update_lead_notedxb('Admin',x, message, edit.status, edit.sub_status)
    try:
        if z == 'Instagram' or z == 'Facebook' or z == 'TikTok' or z == 'Snapchat' or z == 'Messenger':
            z = 'Social Media'
        else:
            pass
        first = lead_update_dubai_log(previous_agent, edit.contact_name, edit.contact_number, 'Lead Lost', z.replace("%20", " "), edit.refno+' reassigned to '+y)
        second = lead_update_dubai_log(y, edit.contact_name, edit.contact_number, 'Assigned', z.replace("%20", " "), edit.refno+' reassigned from '+previous_agent)
    except:
        pass
    session.close()
    return jsonify(success=True)






@handleleadsdxb.route('/all_contacts/dxb',methods = ['GET','POST'])
@login_required
def all_contactsdxb():
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    get_contacts = session.query(Contactsdubai).filter(or_(Contactsdubai.created_by == current_user.username,Contactsdubai.assign_to == current_user.username, current_user.is_admin == True, current_user.listing == True))
    all_contacts = []
    for contact in get_contacts:
        contactObj = {}
        contactObj['refno'] = contact.refno
        contactObj['name'] = str(contact.first_name + ' ' + contact.last_name)
        contactObj['contact'] = contact.number
        contactObj['email'] = contact.email
        contactObj['nationality'] = contact.nationality
        all_contacts.append(contactObj)
    session.close()
    return jsonify({'all_contacts':all_contacts})

def notesdxb(listid):
    with open(os.path.join(NOTES,listid+'.json'), 'w') as f:
        data = {}
        data['notes'] = []
        json.dump(data, f)

def update_lead_notedxb(username, listid, com, status, substatus):
    username = username.replace("%20"," ")
    com = com.replace("%20"," ")
    substatus = substatus.replace("%20"," ")
    with open(os.path.join(NOTES, listid+'.json'),'r+') as file:
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

@handleleadsdxb.route('/all_leadsdxb/<variable>',methods = ['GET','POST'])
@login_required
def view_leadsdxb(variable):
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    lead = session.query(Leadsdubai).filter_by(refno = variable).first()
    all_lead = []
    leadObj = {}
    leadObj = vars(lead)
    leadObj.pop('_sa_instance_state')
    all_lead.append(leadObj)
    session.close()
    return jsonify({'lead':all_lead})

@handleleadsdxb.route('/all_notes_dxb/<variable>',methods = ['GET','POST'])
@login_required
def view_notes_dxb(variable):
    notes = get_notes(variable)
    all_notes = []
    if 'l' in variable.lower():
        for i in notes:
            noteObj = {}
            noteObj['date'] = i['date']
            noteObj['time'] = i['time']
            noteObj['user'] = i['user']
            noteObj['comment'] = i['comment']
            noteObj['status'] = i['status']
            noteObj['substatus'] = i['substatus']
            all_notes.append(noteObj)
    return jsonify({'notes': all_notes})

def get_notes(listid):
    f = open(os.path.join(NOTES,listid+'.json'))
    columns = json.load(f)
    con = columns["notes"]
    return con

@handleleadsdxb.route('/post_leaddxb_note/<list_id>/<com>/<status>/<substatus>',methods = ['GET','POST'])
@login_required
def post_leaddxb_note(list_id,com,status,substatus):
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    a = session.query(Leadsdubai).filter_by(refno = list_id).first()
    a.sub_status = substatus.replace("%20"," ")
    a.status = status
    
    session.commit()
    try:
        pass
        x = edit_lead_agent_dubai(current_user.username, a.contact_number)
    except:
        pass
    update_lead_notedxb(current_user.username,list_id,com,status,substatus)
    update_user_note(current_user.username,list_id,status,substatus)
    session.close()
    return jsonify(success=True)

# Pre-leads module

@handleleadsdxb.route('/pre-leads-dxb',methods = ['GET','POST'])
@login_required
def display_pre_leadsdxb():   
    if current_user.dubai == False or current_user.qa == False:
        return abort(404)
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    data = []
    if current_user.viewall == True:
        for r in session.query(Leadsdubai).filter(Leadsdubai.street == '1'):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            new['created_date'] = new['created_date'][:16]
            new['lastupdated'] = new['lastupdated'][:16]
            edit_btn =  '<a href="/edit_leaddxb/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a><button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            if new['sub_status'] == "Follow up":
                followupBG = 'background-color:rgba(19, 132, 150,0.7);border-radius:20px;box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-webkit-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-moz-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);'
            else:
                followupBG = ""
            reassign_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#reassignModal"  onclick="pre_assign_lead('+"'"+new['refno']+"'"+')"><i class="bi bi-forward-fill"></i></button>'
            new["edit"] = "<div style='display:flex;"+followupBG+"'>"+edit_btn +'<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+reassign_btn+"</div>"
            data.append(new)
    else:
        return abort(404)
    f = open('pre_leads_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    all_sale_users = db.session.query(User).filter(and_(User.sale == True, User.dubai == True)).all()
    session.close()
    return render_template('pre_leadsdubai.html', data = data , columns = columns, user=current_user.username, all_sale_users = all_sale_users)

@handleleadsdxb.route('/pre_assign_leadsdxb_execute/<x>/<y>') #From Pre-Leads
@login_required
def reassign_btn_execute(x, y):
    Session = sessionmaker(bind=db.get_engine(bind='fourth'))
    session = Session()
    if current_user.sale == False or current_user.edit == False:
        return abort(404) 
    edit =session.query(Leadsdubai).filter_by(refno=x).first()
    edit.street = '0'
    edit.agent = y
    edit.lastupdated = datetime.now()+timedelta(hours=4)
    session.commit()
    if (edit.contact_name!= "" or edit.contact_name!= None):
        get_agent = db.session.query(User).filter_by(username = edit.agent).first()
        try:
            etisy_message(edit.agent,edit.contact_name,get_agent.number,edit.contact_number, edit.refno, edit.locationtext, edit.building, edit.lead_type)
        except:
            pass
    else:
        pass
    message = "Lead assigned to "+y
    if edit.locationtext != '':
        message += ' in '+edit.locationtext
    else:
        pass
    if edit.building != '':
        message += ', '+edit.building
    else:
        pass
    try:
        lesgetit = lead_update_dubai_log(edit.agent, edit.contact_name, edit.contact_number, 'Assigned', edit.source, 'via Pre-Leads')
    except:
        pass
    update_lead_notedxb('Admin',x, message, edit.status, edit.sub_status)
    session.close()
    return jsonify(success=True)