from operator import methodcaller
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import Leads, Properties
from forms import AddLeadForm, BuyerLead, DeveloperLead
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import datetime,time
from functions import assign_lead, logs, notes, update_note
from sqlalchemy import or_

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
    if current_user.viewall == True:
        for r in db.session.query(Leads).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            #for k in ['photos','commercialtype','title','description','unit','plot','street','sizeunits','price','rentpriceterm','pricecurrency','totalclosingfee','annualcommunityfee','lastupdated','contactemail','contactnumber','locationtext','furnished','propertyamenities','commercialamenities','geopoint','bathrooms','price_on_application','rentispaid','permit_number','view360','video_url','completion_status','source','owner']: new.pop(k)
            if current_user.edit == True:
                edit_btn =  '<a class="btn btn-primary si" href="/edit_lead/'+str(new['type'])+'/'+str(new['refno'])+'"><i class="bi bi-pencil"></i></a>'
            else:
                edit_btn = ''
            if new['agent'] == current_user.username and new['sub_status'] == "In progress":
                followup = '<button onclick="follow_up('+"'"+new['refno']+"'"+')" class="btn btn-info si" style="color:white;"><i class="bi bi-basket2"></i></button>'
            else:
                followup = ""
            new["edit"] = "<div style='display:flex;'>"+edit_btn +'<button class="btn btn-danger si"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-aspect-ratio"></i></button>'+'<button class="btn btn-warning si" style="color:white;" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-plus"></i></button>'+followup+"</div>"
            data.append(new)
    else:
        for r in db.session.query(Leads).filter(or_(Leads.created_by == current_user.username,Leads.agent == current_user.username)):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            #for k in ['photos','commercialtype','title','description','unit','plot','street','sizeunits','price','rentpriceterm','pricecurrency','totalclosingfee','annualcommunityfee','lastupdated','contactemail','contactnumber','locationtext','furnished','propertyamenities','commercialamenities','geopoint','bathrooms','price_on_application','rentispaid','permit_number','view360','video_url','completion_status','source','owner']: new.pop(k)
            if current_user.edit == True:
                edit_btn =  '<a class="btn btn-primary si" href="/edit_lead/'+str(new['type'])+'/'+str(new['refno'])+'"><i class="bi bi-pencil"></i></a>'
            else:
                edit_btn = ''
            if new['agent'] == current_user.username and new['sub_status'] == "In progress":
                followup = '<button onclick="follow_up('+"'"+new['refno']+"'"+')" class="btn btn-info si" style="color:white;"><i class="bi bi-basket2"></i></button>'
            else:
                followup = ""
            new["edit"] = "<div style='display:flex;'>"+edit_btn +'<button class="btn btn-danger si"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-aspect-ratio"></i></button>'+'<button class="btn btn-warning si" style="color:white;" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-plus"></i></button>'+followup+"</div>"
            data.append(new)

    f = open('lead_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('leads.html', data = data , columns = columns, user=current_user.username)



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
        locationtext = file_data[form.locationtext.data]
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
        newlead = Leads(type="secondary",role=role,source=source,contact = contact,contact_name = contact_name,contact_number = contact_number,contact_email = contact_email,nationality = nationality,time_to_contact = time_to_contact,agent = agent,enquiry_date = enquiry_date,purpose = purpose,propertyamenities = propertyamenities,created_by=current_user.username,status = status,sub_status = sub_status,property_requirements = property_requirements,locationtext = locationtext,building = building,subtype = subtype,min_beds = min_beds,max_beds = max_beds,min_price = min_price,max_price = max_price,unit = unit,plot = plot,street = street,size = size,lead_type=lead_type)
        db.session.add(newlead)
        db.session.commit()
        db.session.refresh(newlead)
        newlead.refno = 'UNI-L-'+str(newlead.id)
        db.session.commit()
        logs(current_user.username,'UNI-L-'+str(newlead.id),'Added')
        notes('UNI-L-' + str(newlead.id))
        assign_lead(current_user.username,'UNI-L-'+str(newlead.id),newlead.sub_status)
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
        locationtext = file_data[form.locationtext.data]
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
        newlead = Leads(type="developer",role=role,source=source,contact = contact,contact_name = contact_name,contact_number = contact_number,contact_email = contact_email,nationality = nationality,time_to_contact = time_to_contact,agent = agent,enquiry_date = enquiry_date,purpose = purpose,propertyamenities = propertyamenities,created_by=current_user.username,status = status,sub_status = sub_status,property_requirements = property_requirements,locationtext = locationtext,building = building,subtype = subtype,min_beds = min_beds,max_beds = max_beds,min_price = min_price,max_price = max_price,unit = unit,plot = plot,street = street,size = size,lead_type=lead_type)
        db.session.add(newlead)
        db.session.commit()
        db.session.refresh(newlead)
        newlead.refno = 'UNI-L-'+str(newlead.id)
        db.session.commit()
        logs(current_user.username,'UNI-L-'+str(newlead.id),'Added')
        notes('UNI-L-' + str(newlead.id))
        assign_lead(current_user.username,'UNI-L-'+str(newlead.id),newlead.sub_status)
        update_note(current_user.username,property_requirements, "Added"+"UNI-L-"+str(newlead.id)+"lead For viewing")
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
    form.locationtext.data = list(mydict.keys())[list(mydict.values()).index(edit.locationtext)]
    if request.method == 'POST':
        form.populate_obj(edit)
        edit.propertyamenities = ",".join(form.propertyamenities.data)
        edit.locationtext = mydict[new]
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
    stats_open = ['In progress','Not yet contacted','Called no reply','Follow up','Offer made','Interested','Interested to meet','Not interested']
    stats_closed = ['successful', 'unsuccessful']
    if a == 'Open':
        for i in stats_open:
            status.append((i,i))
    elif a == 'Closed': 
        for i in stats_closed:
            status.append((i,i))
    return jsonify({'status':status})

    