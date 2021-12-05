from operator import methodcaller
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import except_all
from models import Leads, Properties,Contacts
from forms import AddLeadForm, BuyerLead, DeveloperLead
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import date, datetime,time
from functions import assign_lead, logs, notes, update_note,lead_email
from sqlalchemy import or_
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
    if current_user.viewall == True and current_user.is_admin == True:
        for r in db.session.query(Leads).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            #for k in ['photos','commercialtype','title','description','unit','plot','street','sizeunits','price','rentpriceterm','pricecurrency','totalclosingfee','annualcommunityfee','lastupdated','contactemail','contactnumber','locationtext','furnished','propertyamenities','commercialamenities','geopoint','bathrooms','price_on_application','rentispaid','permit_number','view360','video_url','completion_status','source','owner']: new.pop(k)
            if current_user.edit == True:
                if r.created_by == current_user.username or r.agent == current_user.username:
                    edit_btn =  '<a href="/edit_lead/'+str(new['type'])+'/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
                else:
                    edit_btn = ''
            else:
                edit_btn = ''
            if new['agent'] == current_user.username and new['sub_status'] == "In progress":
                followup = '<button onclick="follow_up('+"'"+new['refno']+"'"+')" class="btn-info si2" style="color:white;"><i class="bi bi-plus-circle"></i></button>'
            else:
                followup = ""
            viewing = '<button onclick="request_viewing('+"'"+new['refno']+"'"+')" class="btn-success si2" style="color:white;"><i class="bi bi-eye"></i></button>'
            new["edit"] = "<div style='display:flex;'>"+edit_btn +'<button class="btn-danger si2" data-toggle="modal" data-target="#viewModal"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-arrows-fullscreen"></i></button>'+'<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+followup+viewing+"</div>"
            data.append(new)
    else:
        for r in db.session.query(Leads).filter(or_(Leads.created_by == current_user.username,Leads.agent == current_user.username)):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            #for k in ['photos','commercialtype','title','description','unit','plot','street','sizeunits','price','rentpriceterm','pricecurrency','totalclosingfee','annualcommunityfee','lastupdated','contactemail','contactnumber','locationtext','furnished','propertyamenities','commercialamenities','geopoint','bathrooms','price_on_application','rentispaid','permit_number','view360','video_url','completion_status','source','owner']: new.pop(k)
            if current_user.edit == True:
                if r.created_by == current_user.username or r.agent == current_user.username:
                    edit_btn =  '<a href="/edit_lead/'+str(new['type'])+'/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
                else:
                    edit_btn = ''
            else:
                edit_btn = ''
            if new['agent'] == current_user.username and new['sub_status'] == "In progress":
                followup = '<button onclick="follow_up('+"'"+new['refno']+"'"+')" class="btn-info si2" style="color:white;"><i class="bi bi-plus-circle"></i></button>'
            else:
                followup = ""
            viewing = '<button onclick="request_viewing('+"'"+new['refno']+"'"+')" class="btn-success si2" style="color:white;"><i class="bi bi-eye"></i></button>'
            new["edit"] = "<div style='display:flex;'>"+edit_btn +'<button class="btn-danger si2" data-toggle="modal" data-target="#viewModal"  onclick="view_leads('+"'"+new['refno']+"'"+')"><i class="bi bi-arrows-fullscreen"></i></button>'+'<button class="btn-warning si2" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-text"></i></button>'+followup+viewing+"</div>"
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
        newlead = Leads(type="secondary",created_date=created_date,role=role,source=source,contact = contact,contact_name = contact_name,contact_number = contact_number,contact_email = contact_email,nationality = nationality,time_to_contact = time_to_contact,agent = agent,enquiry_date = enquiry_date,purpose = purpose,propertyamenities = propertyamenities,created_by=current_user.username,status = status,sub_status = sub_status,property_requirements = property_requirements,locationtext = locationtext,building = building,subtype = subtype,min_beds = min_beds,max_beds = max_beds,min_price = min_price,max_price = max_price,unit = unit,plot = plot,street = street,size = size,lead_type=lead_type)
        db.session.add(newlead)
        db.session.commit()
        db.session.refresh(newlead)
        newlead.refno = 'UNI-L-'+str(newlead.id)
        db.session.commit()
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
        newlead = Leads(type="developer",created_date=created_date,role=role,source=source,contact = contact,contact_name = contact_name,contact_number = contact_number,contact_email = contact_email,nationality = nationality,time_to_contact = time_to_contact,agent = agent,enquiry_date = enquiry_date,purpose = purpose,propertyamenities = propertyamenities,created_by=current_user.username,status = status,sub_status = sub_status,property_requirements = property_requirements,locationtext = locationtext,building = building,subtype = subtype,min_beds = min_beds,max_beds = max_beds,min_price = min_price,max_price = max_price,unit = unit,plot = plot,street = street,size = size,lead_type=lead_type)
        db.session.add(newlead)
        db.session.commit()
        db.session.refresh(newlead)
        newlead.refno = 'UNI-L-'+str(newlead.id)
        db.session.commit()
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
    stats_open = ['In progress','Not yet contacted','Called no reply','Follow up','Offer made','Viewing arranged','Viewing Done','Interested','Interested to meet','Not interested','Needs time','Client not reachable']
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


@handleleads.route('/reassign_leads/<personA>/<personB>')
@login_required
def reassign_leads(personA,personB):
    all_leads = db.session.query(Leads).filter(or_(Leads.agent == personA,Leads.created_by == personA))
    for i in all_leads:
        i.agent = personB
        i.created_by = personB
        db.session.commit()
    return "ok"

@handleleads.route('/marketing_leads',methods = ['GET','POST'])
@login_required
def marketing_leads():
    a = [('Villa', 'Yas Island', 'Yas Acres', 'Aems', 'Mall', 971557551323, 'nan', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Urba', 'Kiani', 971552933726, 'nan', 'FB'), ('Villa', 'Yas Island', 'Yas Acres', 'nazneen', '_', 971569401663, 'nazneenjn@hotmail.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Noor', '_', 971507025151, 'Nooralharbi@hotmail.co.uk', 'TK'), ('Apartment', 'Yas Island', 'La Perla', 'Hossam', 'Eid', 971525527015, 'dentaleagle2011@gmail.com', 'FB'), ('Apartment', 'Yas Island', 'La Perla', 'Jaswinder', 'Singh', 971501014835, 'nan', 'FB'), ('Villa', 'Yas Island', 'Yas Acres', '___', '_', 971556435111, 'nan', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Ghazi', '_', 971507094333, 'izahg7@gmail.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Zainab', '_', 971521113340, 'Zainabalajmi1996@gmail.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Hazaa', 'Albreki', 971501314900, 'Uae.ha1994@hotmail.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Talal', '_', 971507255516, 'T.m.alyammahi@gmail.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Alam', '_', 971545932767, 'khanalamzaib350@gmail.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Ghazi', '_', 971507094333, 'izahg7@gmail.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Zainab', '_', 971521113340, 'Zainabalajmi1996@gmail.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Hazaa', 'Albreki', 971501314900, 'Uae.ha1994@hotmail.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Talal', '_', 971507255516, 'T.m.alyammahi@gmail.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'Ehsaan', 'ali', 971505149663, 'Eali786@icloud.com', 'TK'), ('Villa', 'Yas Island', 'Yas Acres', 'sammi', 'sommers', 971545224401, 'boss55.sommers@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Bahmed', '_', 33634621102, 'karimrx59@hotmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Mushtaq', 'Ahmed', 971504634222, 'musthtaqahmedmm7@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Marwan', '_', 971557777718, 'Marwanh330@gmail.com', 'TK'), ('Apartment', 'Yas Island', 'Mayan', 'Arif', '_', 971502330393, 'Amehmood73@gmail.con', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'riyadmansoor', '_', 971502097058, 'riyasmansoormk@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Jannat', 'Kayani', 971544509864, 'jannatkayani1997@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Mohamad', 'badar', 971554434656, 'Mohammadbadar@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Aisha', '', 971502110660, 'Alhammadi.aisha12@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'khaled', '', 971554250060, 'khaled.hussein1199@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Peter', 'Nabil', 971585301190, 'peter.nabil@hotmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Naveed', 'khan', 971569781139, 'daulatkhel@ymail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Vasil', 'Ahmed', 971558756609, 'vasil007@rediffmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Hamid', '', 971508877001, 'Hamidafsari62@gmail.com', 'TK'), ('Apartment', 'Yas Island', 'Mayan', 'Ajmal', '_', 971506177346, 'Ajmal.dubaisigns@gmail.com', 'TK'), ('Apartment', 'Yas Island', 'Mayan', 'Rebto', 'Adame', 971506177346, 'rebtoadame@gmail.com', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Habib', 'Adnan', 971522408377, 'mm3947986@gmail.com', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Ghamdan', 'Al Kherbash', 971552017522, 'ghamdan.alkherbash@hotmail.com', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Hamonawit', 'Maru', 251913518504, 'Tgt0433@gimail.com', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Ghzanfar', 'Iqbal', 971508097389, 'ghzanfariqbal786@gmail.com', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Malek', '_', 971555480017, 'malik_hajeer@yahoo.com', 'TK'), ('Apartment', 'Yas Island', 'Mayan', 'Syed', '_', 971504984042, 'myellow10@yahoo.com', 'TK'), ('Apartment', 'Yas Island', 'Mayan', 'Yesmien', 'Sheik', 971562573502, 'yesmiensheikh@gmail.com', 'TK'), ('Apartment', 'Yas Island', 'Mayan', 'Sammi', 'Somers', 971545224401, 'boss55.sommers@gmail.com', 'TK'), ('Apartment', 'Yas Island', 'Mayan', 'Hussain', '_', 971506884113, 'hussain88804@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Saddam', 'Hossain', 971566431816, 'saddamhossian64@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Attiq', 'Ahmed', 971521825261, 'ateeqsheikh031@gmail.com', 'TK'), ('Apartment', 'Yas Island', 'Mayan', 'Nahla', 'Aljanabi', 14508254054, 'falah1949@msn.com', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Emmie', 'Salonga', 971586161243, 'emmiesalonga@gmail.com', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Alamin', 'Hossain', 971554242684, 'alameen19911@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Sophia', 'Nantongo', 256752356964, 'ntongos229@gmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Amjad', 'Khan', 919523866633, 'alsifakhatun0045@gmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'LJP', '_', 97143382420, 'lakshmanpiyatunga@hotmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Adelaida', 'Zacarias', 971563670751, 'adelaydaabadzacarias@gmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Mohammed', 'Abdul', 971567998371, 'aleemrizwan30@gmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Vera', 'James', 919168838300, 'jvchicos@gmail.com', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Lucja', 'Koryczan', 971565378603, 'luck.oryczan@gmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2','Gamr','Najy' ,971544174328, 'gamr2030@icloud.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Abdulla', '_', 971505920054, 'abdullaalmujaini511@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Hbi.dbdibd', '_', 971549995596, 'nan', 'Inst'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Ahmed', 'Talal', 971566972055, 'ahmedtalal308@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Diya', 'Yaaeen', 971563705467, 'dyeeea@hotmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Azizunnisa', 'Shaikh', 971561771076, '_', 'Inst'), ('Apartment', 'Yas Island', 'Mayan', 'Romansy', '_', 971501212494, '_', 'Inst'), ('Apartment', 'Yas Island', 'Mayan', 'Alla','Tahrawi', 971527077337, 'alla.tahrawi@methaq.ae', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Amna', 'Tufail', 971501942073, 'amnatufail@gmail.com', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Non','Al Gendy', 971557659399, 'nonaelgendy373@hotmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Salina', 'Salim', 919946518877, 'salinasalim1951@gmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Michele', '_', 971544865689, 'micheleahmedal@gmail.com', 'TK'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Ramadan', 'Matar', 971506412184, 'moatazsohail23@gmail.com', 'TK'), ('Apartment', 'Yas Island', 'Mayan', 'Chadd', 'Dinham', 971564408621, 'Chaddinoz@yahoo.com.au', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'Dave', 'M', 97158539849, 'Davidmhoul@gmail.com', 'FB'), ('Villa', 'Saadiyat Island', 'Mamsha Al Saadiyat', 'Veny', 'Shah', 971528274261, 'nan', 'FB'), ('Apartment', 'Yas Island', 'Mayan', 'DreamLife', '_', 971508293200, 'nan', 'FB'), ('Villa', 'Saadiyat Island', 'Mamsha Al Saadiyat', 'Yěpiñķ', 'Gől', 971547412948, 'monishatamang11@gmail.com', 'FB'), ('Apartment', 'Yas Island', 'Water’s Edge', 'mohammad', 'al', 971553033878, 'rubooahouran@gmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'shaima', 'almarri', 971559229882, 'nan', 'Inst'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'mihab', 'local', 971506336654, 'nan', 'Inst'), ('Apartment', 'Yas Island', 'Water’s Edge','Alla','Khalid' ,971527077337,'alla.tahrawe@methaq.ae', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Faisal', 'Alameri', 971054181845, 'falameri2@gmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'AzizMuhammed', '_', 971566929834, 'muhammedaziz786133@gmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'K8', '_', 971502889939, 'Orders8k@gmail.com', 'FB'), ('Villa', 'Al Ghadeer', 'Al Ghadeer 2', 'Mohamed', 'Laribi', 971556660308, 'mohamedlaribi2021@gmail.com', 'FB'), ('Villa', 'Yas Island', 'Yas Acres', 'chadia', '_', 971582591544, 'nan', 'Inst'), ('Apartment', 'Yas Island', 'Water’s Edge', 'khaled', '_', 971542222992, 'nan', 'FB')]
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
        newlead = Leads(type="secondary",created_date=created_date,source=source,contact = contact,contact_name = contact_name,contact_number = contact_number,contact_email = contact_email,agent = agent,enquiry_date = enquiry_date,created_by=current_user.username,locationtext = locationtext,building = building,subtype = subtype,lead_type="Buy")
        db.session.add(newlead)
        db.session.commit()
        db.session.refresh(newlead)
        newlead.refno = 'UNI-L-'+str(newlead.id)
        db.session.commit()
        logs(current_user.username,'UNI-L-'+str(newlead.id),'Added')
        notes('UNI-L-' + str(newlead.id))
    return "ok"



