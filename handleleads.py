from curses.ascii import NUL
from operator import methodcaller
from xml.dom.minicompat import EmptyNodeList
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import except_all
from models import Leads, Properties,Contacts, User
from forms import AddLeadForm, BuyerLead, DeveloperLead
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import date, datetime,time
from functions import assign_lead, logs, notes, update_note,lead_email
from sqlalchemy import or_,and_
import csv
from datetime import datetime, timedelta

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)




db = SQLAlchemy()

handleleads = Blueprint('handleleads', __name__, template_folder='templates')



@handleleads.route('/leads',methods = ['GET','POST'])
@login_required
def display_leads():   
    if current_user.sale == False:
        return abort(404)
    data = []
    if current_user.team_members == "QC" and current_user.sale == True and current_user.is_admin == False:
        for r in db.session.query(Leads).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            if new['sub_status'] != "Flag":
                flag = '<button onclick="flag_lead('+"'"+new['refno']+"'"+')" class="btn-danger si2" style="color:white;"><i class="bi bi-flag"></i></button>'
            else:
                flag = ''
            #for k in ['photos','title','description','plot','street','rentpriceterm','contactemail','contactnumber','furnished','privateamenities','commercialamenities','geopoint','unit','permit_number','view360','video_url','completion_status','source','owner','tenant','parking','featured','offplan_status','tenure','expiry_date','deposit','commission','price_per_area','plot_size']: new.pop(k)
            new["edit"] = '<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+flag+'<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#reassignModal"  onclick="reassign_lead('+"'"+new['refno']+"'"+')">R</button></div>'
            
            data.append(new)
        f = open('lead_headers.json')
        columns = json.load(f)
        columns = columns["headers"]
        all_lead_users = db.session.query(User).filter_by(sale = True).all()
        return render_template('leads.html', data = data , columns = columns, user=current_user.username,all_lead_users=all_lead_users)
    if current_user.viewall == True and current_user.is_admin == True:
        for r in db.session.query(Leads).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            if current_user.edit == True:
                edit_btn =  '<a href="/edit_lead/'+str(new['type'])+'/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a><button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            else:
                edit_btn = ''
            if new['sub_status'] != "Flag":
                flag = '<button onclick="flag_lead('+"'"+new['refno']+"'"+')" class="btn-danger si2" style="color:white;"><i class="bi bi-flag"></i></button>'
            else:
                flag = ''
            if new['agent'] == current_user.username and new['sub_status'] == "In progress":
                followup = '<button onclick="follow_up('+"'"+new['refno']+"'"+')" class="btn-info si2" style="color:white;"><i class="bi bi-plus-circle"></i></button>'
                followupBG = 'background-color:rgba(19, 132, 150,0.7);border-radius:20px;box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-webkit-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-moz-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);'
            else:
                followup = ""
                followupBG = ""
            viewing = '<button onclick="request_viewing('+"'"+new['refno']+"'"+')" class="btn-success si2" style="color:white;"><i class="bi bi-eye"></i></button>'
            new["edit"] = "<div style='display:flex;"+followupBG+"'>"+edit_btn +'<button class="btn-danger si2" data-toggle="modal" data-target="#viewModal"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-arrows-fullscreen"></i></button>'+'<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+followup+viewing+flag+"</div>"
            data.append(new)
    elif current_user.viewall == True and current_user.team_lead == True:
        for r in db.session.query(Leads).filter(or_(Leads.created_by == current_user.username,Leads.agent == current_user.username)):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            if current_user.edit == True:
                edit_btn =  '<a href="/edit_lead/'+str(new['type'])+'/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a><button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            else:
                edit_btn = ''
            if new['sub_status'] != "Flag":
                flag = '<button onclick="flag_lead('+"'"+new['refno']+"'"+')" class="btn-danger si2" style="color:white;"><i class="bi bi-flag"></i></button>'
            else:
                flag = ''
            if new['agent'] == current_user.username and new['sub_status'] == "In progress":
                followup = '<button onclick="follow_up('+"'"+new['refno']+"'"+')" class="btn-info si2" style="color:white;"><i class="bi bi-plus-circle"></i></button>'
                followupBG = 'background-color:rgba(19, 132, 150,0.7);border-radius:20px;box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-webkit-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-moz-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);'
            else:
                followup = ""
                followupBG = ""
            viewing = '<button onclick="request_viewing('+"'"+new['refno']+"'"+')" class="btn-success si2" style="color:white;"><i class="bi bi-eye"></i></button>'
            new["edit"] = "<div style='display:flex;"+followupBG+"'>"+edit_btn +'<button class="btn-danger si2" data-toggle="modal" data-target="#viewModal"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-arrows-fullscreen"></i></button>'+'<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+followup+viewing+flag+"</div>"
            data.append(new)
        for i in current_user.team_members.split(','):
            for r in db.session.query(Leads).filter(or_(Leads.created_by == i,Leads.agent == i)):
                row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
                new = row2dict(r)
                if current_user.edit == True:
                    edit_btn =  '<a href="/edit_lead/'+str(new['type'])+'/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a><button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
                else:
                    edit_btn = ''
                if new['sub_status'] != "Flag":
                    flag = '<button onclick="flag_lead('+"'"+new['refno']+"'"+')" class="btn-danger si2" style="color:white;"><i class="bi bi-flag"></i></button>'
                else:
                    flag = ''
                if new['agent'] == current_user.username and new['sub_status'] == "In progress":
                    followup = ""
                    followupBG = 'background-color:rgba(19, 132, 150,0.7);border-radius:20px;box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-webkit-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);-moz-box-shadow: 0px 0px 17px 7px rgba(19,132,150,0.89);'
                else:
                    followup = ""
                    followupBG = ""
                viewing = '<button onclick="request_viewing('+"'"+new['refno']+"'"+')" class="btn-success si2" style="color:white;"><i class="bi bi-eye"></i></button>'
                new["edit"] = "<div style='display:flex;"+followupBG+"'>"+edit_btn +'<button class="btn-danger si2" data-toggle="modal" data-target="#viewModal"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-arrows-fullscreen"></i></button>'+'<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+followup+viewing+flag+"</div>"
                data.append(new)
    else:
        for r in db.session.query(Leads).filter(or_(Leads.created_by == current_user.username,Leads.agent == current_user.username)):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            #for k in ['photos','commercialtype','title','description','unit','plot','street','sizeunits','price','rentpriceterm','pricecurrency','totalclosingfee','annualcommunityfee','lastupdated','contactemail','contactnumber','locationtext','furnished','propertyamenities','commercialamenities','geopoint','bathrooms','price_on_application','rentispaid','permit_number','view360','video_url','completion_status','source','owner']: new.pop(k)
            if current_user.edit == True:
                if r.created_by == current_user.username or r.agent == current_user.username:
                    edit_btn =  '<a href="/edit_lead/'+str(new['type'])+'/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a><button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
                else:
                    edit_btn = ''
            else:
                edit_btn = ''
            if new['sub_status'] != "Flag":
                flag = '<button onclick="flag_lead('+"'"+new['refno']+"'"+')" class="btn-danger si2" style="color:white;"><i class="bi bi-flag"></i></button>'
            else:
                flag = ''
            if new['agent'] == current_user.username and new['sub_status'] == "In progress":
                followup = '<button onclick="follow_up('+"'"+new['refno']+"'"+')" class="btn-info si2" style="color:white;"><i class="bi bi-plus-circle"></i></button>'
                followupBG = 'background-color:#138496;background-color:rgba(19, 132, 150,0.7);border-radius:20px;'
            else:
                followupBG = ""
                followup = ""
            viewing = '<button onclick="request_viewing('+"'"+new['refno']+"'"+')" class="btn-success si2" style="color:white;"><i class="bi bi-eye"></i></button>'
            new["edit"] = "<div style='display:flex; "+followupBG+"'>"+edit_btn +'<button class="btn-danger si2" data-toggle="modal" data-target="#viewModal"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-arrows-fullscreen"></i></button>'+'<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+followup+viewing+flag+"</div>"
            data.append(new)
    f = open('lead_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('leads.html', data = data , columns = columns, user=current_user.username)

@handleleads.route('/reassign_lead/<variable>/<user>', methods = ['GET','POST'])
@login_required
def reassign_lead(variable, user):
    if current_user.sale == False or current_user.edit == False:
        return abort(404) 
    edit = db.session.query(Leads).filter_by(refno=variable).first()
    edit.agent = user
    db.session.commit()
    return redirect(url_for('handleleads.display_leads'))

@handleleads.route('/reassign_lead/<variable>', methods = ['GET','POST'])
@login_required
def reassign_lead_nouser(variable):
    if current_user.sale == False or current_user.edit == False:
        return abort(404) 
    return redirect(url_for('handleleads.display_leads'))

@handleleads.route('/delete_lead/<variable>', methods = ['GET','POST'])
@login_required
def delete_lead(variable):
    if current_user.sale == False or current_user.edit == False:
        return abort(404) 
    delete = db.session.query(Leads).filter_by(refno=variable).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('handleleads.display_leads'))


@handleleads.route('/add_lead_buyer/', methods = ['GET','POST'])
@login_required
def add_lead_buyer():
    if current_user.sale == False:
        return abort(404)  
    form = BuyerLead()
    if request.method == 'POST':
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
        newlead = Leads(type="secondary",lastupdated=lastupdated,created_date=created_date,role=role,source=source,contact = contact,contact_name = contact_name,contact_number = contact_number,contact_email = contact_email,nationality = nationality,time_to_contact = time_to_contact,agent = agent,enquiry_date = enquiry_date,purpose = purpose,propertyamenities = propertyamenities,created_by=current_user.username,status = status,sub_status = sub_status,property_requirements = property_requirements,locationtext = locationtext,building = building,subtype = subtype,min_beds = min_beds,max_beds = max_beds,min_price = min_price,max_price = max_price,unit = unit,plot = plot,street = street,size = size,lead_type=lead_type)
        db.session.add(newlead)
        db.session.commit()
        db.session.refresh(newlead)
        newlead.refno = 'UNI-L-'+str(newlead.id)
        db.session.commit()
        #get_agent = db.session.query(User).filter_by(username = agent).first()
        #deploy_message(agent,contact_name,get_agent.number,contact_number, newlead.refno, locationtext, building, lead_type)
        logs(current_user.username,'UNI-L-'+str(newlead.id),'Added')
        notes('UNI-L-' + str(newlead.id))
        assign_lead(current_user.username,'UNI-L-'+str(newlead.id),newlead.sub_status)
        if property_requirements != "":
            update_note(current_user.username,property_requirements, "Added"+" UNI-L-"+str(newlead.id)+" lead for viewing")
        lead_email(current_user.email, 'UNI-L-' + str(newlead.id))

        return redirect(url_for('handleleads.display_leads'))
    return render_template('add_lead_buyer.html', form=form, user = current_user.username)

@handleleads.route('/add_lead_developer/', methods = ['GET','POST'])
@login_required
def add_lead_developer():
    if current_user.sale == False:
        return abort(404)  
    form = DeveloperLead()
    if request.method == 'POST':
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
        newlead = Leads(type="developer",lastupdated=lastupdated,created_date=created_date,role=role,source=source,contact = contact,contact_name = contact_name,contact_number = contact_number,contact_email = contact_email,nationality = nationality,time_to_contact = time_to_contact,agent = agent,enquiry_date = enquiry_date,purpose = purpose,propertyamenities = propertyamenities,created_by=current_user.username,status = status,sub_status = sub_status,property_requirements = property_requirements,locationtext = locationtext,building = building,subtype = subtype,min_beds = min_beds,max_beds = max_beds,min_price = min_price,max_price = max_price,unit = unit,plot = plot,street = street,size = size,lead_type=lead_type)
        db.session.add(newlead)
        db.session.commit()
        db.session.refresh(newlead)
        newlead.refno = 'UNI-L-'+str(newlead.id)
        db.session.commit()
        #get_agent = db.session.query(User).filter_by(username = agent).first()
        #deploy_message(agent,contact_name,get_agent.number,contact_number, newlead.refno, locationtext, building, lead_type)
        logs(current_user.username,'UNI-L-'+str(newlead.id),'Added')
        notes('UNI-L-' + str(newlead.id))
        assign_lead(current_user.username,'UNI-L-'+str(newlead.id),newlead.sub_status)
        if property_requirements != "":
            update_note(current_user.username,property_requirements, "Added"+" UNI-L-"+str(newlead.id)+" lead for viewing")
        return redirect(url_for('handleleads.display_leads'))
    return render_template('add_lead_developer.html', form=form, user = current_user.username)


@handleleads.route('/edit_lead/<markettype>/<var>', methods = ['GET','POST'])
@login_required
def edit_lead(markettype,var):
    if current_user.sale == False or current_user.edit == False:
        return abort(404) 
    edit = db.session.query(Leads).filter_by(refno = var).first()
    if markettype == "secondary":
        template = "add_lead_buyer.html" 
        form = BuyerLead(obj = edit)
    elif markettype == "developer":
        template = "add_lead_developer.html" 
        form = DeveloperLead(obj = edit)
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
        db.session.commit()
        logs(current_user.username,edit.refno,'Edited')
        return redirect(url_for('handleleads.display_leads'))
    if edit.propertyamenities  != None:
        form.propertyamenities.data = edit.propertyamenities.split(',')
    return render_template(template, form=form,building = edit.building,assign=edit.agent, user = current_user.username, sub_status = edit.sub_status)


@handleleads.route('/status/<substatus>',methods = ['GET','POST'])
@login_required
def community(substatus):
    a = substatus
    status = []
    stats_open = ['In progress','Flag','Not yet contacted','Called no reply','Follow up','Offer made','Viewing arranged','Viewing Done','Interested','Interested to meet','Not interested','Needs time','Client not reachable']
    stats_closed = ['Successful', 'Unsuccessful']
    if a == 'Open':
        for i in stats_open:
            status.append((i,i))
    elif a == 'Closed': 
        for i in stats_closed:
            status.append((i,i))
    return jsonify({'status':status})


@handleleads.route('/null_leads',methods = ['GET','POST'])
@login_required
def null_leads():
    for i in db.session.query(Leads).all():
        i.unit = "-"
        db.session.commit()

@handleleads.route('/flag_lead/<refno>')
@login_required
def flag_leads(refno):
    edit = db.session.query(Leads).filter_by(refno = refno).first()
    edit.sub_status = "Flag"
    db.session.commit()
    return "success"

@handleleads.route('/reassign_leads/<personA>/<personB>')
@login_required
def reassign_leads(personA,personB):
    all_leads = db.session.query(Leads).filter(or_(Leads.agent == personA,Leads.created_by == personA))
    for i in all_leads:
        i.agent = personB
        i.created_by = personB
        db.session.commit()
    return "ok"

@handleleads.route('/reassign_leads70/<personA>/<personB>/<personC>/<personD>/<personE>/<personF>/<personG>/<personH>/<personI>/<personJ>/<personK>/<personL>/<personM>/<personN>/<personZ>') #lesssgooo
@login_required
def reassign_leads70(personA,personB,personC,personD,personE,personF,personG,personH,personI,personJ,personK,personL,personM,personN,personZ):
    all_leads = db.session.query(Leads).filter(or_(Leads.agent == personA,Leads.agent == personB,Leads.agent == personC,Leads.agent == personD,Leads.agent == personE,Leads.agent == personF,Leads.agent == personG,Leads.agent == personH,Leads.agent == personI,Leads.agent == personJ,Leads.agent == personK,Leads.agent == personL,Leads.agent == personM,Leads.agent == personN))
    for i in all_leads:
        i.agent = personZ
        db.session.commit()
    return "ok"

@handleleads.route('/reassign_leads71/<personA>/<personB>/<personC>/<personD>/<personE>') #lesssgooo
@login_required
def reassign_leads71(personA,personB,personC,personD,personE):
    all_leads = db.session.query(Leads).filter(or_(Leads.created_by == personA,Leads.created_by == personB,Leads.created_by == personC,Leads.created_by == personD))
    for i in all_leads:
        i.created_by = personE
        db.session.commit()
    return "ok"

@handleleads.route('/reassign_lastupdated') #lesssgooo
@login_required
def reassign_lastupdated():
    all_leads = db.session.query(Leads).filter(Leads.lastupdated == None)
    for i in all_leads:
        i.lastupdated = i.created_date
        db.session.commit()
    return "ok"

@handleleads.route('/marketing_leads',methods = ['GET','POST'])
@login_required
def marketing_leads():
    a = [('Apartment', 'Al Marina', 'Fairmont Marina Residences','Faheema','_',447981269201, 'Faheemamoosa2002@gmail.com', 'TK'),('Apartment', 'Al Marina', 'Fairmont Marina Residences','Faheem','Kassam',971504429585, 'fhmkassam@globemw.net', 'TK'),('Apartment', 'Al Marina', 'Fairmont Marina Residences','Noon','_',971504100693, 'noonaah2020@gmail.com', 'TK'),('Apartment', 'Al Marina', 'Fairmont Marina Residences','Hatem','Haddad',971508004754, 'arabicdatamining@gmail.com', 'TK'),('Apartment', 'Al Marina', 'Fairmont Marina Residences','Vladimir','_',380672322215, 'vladimirbulankov@gmail.com', 'TK')]
    a.reverse()
    for i in a:
        a = db.session.query(Contacts).filter_by(number = i[5]).first()
        if a == None:
            first_name = i[3]
            last_name = i[4]
            number = i[5]
            email = i[6]
            newcontact = Contacts(first_name=first_name, last_name=last_name ,number=number,email=email, assign_to=current_user.username)
            db.session.add(newcontact)
            db.session.commit()
            db.session.refresh(newcontact)
            newcontact.refno = 'UNI-O-'+str(newcontact.id)
            db.session.commit()
            directory = UPLOAD_FOLDER+'/UNI-O-'+str(newcontact.id)
            if not os.path.isdir(directory):
                os.mkdir(directory)
            contact = newcontact.refno 
        else:
            first_name = a.first_name
            last_name = a.last_name
            number = a.number
            email = a.email
            contact = a.refno 
        contact_name = str(first_name) + " " + str(last_name)
        contact_number = number
        contact_email = email
        agent = "Mohammad_Jbour"
        enquiry_date = datetime.now()
        locationtext = i[1]
        building = i[2]
        subtype = i[0]
        if i[7] == "TK":
            source = "Tiktok"
        elif i[7] == "FB":
            source = "Facebook"
        elif i[7] == "Inst":
            source = "instagram"
        else:
            source = "Company Website"
        created_date = datetime.now()+timedelta(hours=4)
        newlead = Leads(type="secondary",created_date=created_date,source=source,contact = contact,contact_name = contact_name,contact_number = contact_number,contact_email = contact_email,agent = agent,enquiry_date = enquiry_date,created_by=current_user.username,locationtext = locationtext,building = building,subtype = subtype,lead_type="Buy", status = "Open", sub_status = "Follow up")
        db.session.add(newlead)
        db.session.commit()
        print("added_lead")
        db.session.refresh(newlead)
        newlead.refno = 'UNI-L-'+str(newlead.id)
        db.session.commit()
        logs(current_user.username,'UNI-L-'+str(newlead.id),'Added')
        notes('UNI-L-' + str(newlead.id))
    return "ok"

