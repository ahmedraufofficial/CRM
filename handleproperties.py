from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.elements import Null
from models import Properties, Contacts
from forms import AddPropertyForm
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
import glob
from functions import logs, notes, add_user_list
from sqlalchemy import or_, and_
import xml.etree.cElementTree as e
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import json
import re
import sqlite3
import os
import csv
import arabic_reshaper
from bidi.algorithm import get_display


a = os.getcwd()
UPLOAD_FOLDER = os.path.join(a+'/static', 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)




db = SQLAlchemy()

handleproperties = Blueprint('handleproperties', __name__, template_folder='templates')

def dubbizlexml():
    data = []
    for r in db.session.query(Properties).all():
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        data.append(new)

    mapdir = os.getcwd() + '/'   
    f = open(os.path.join(mapdir+'dubizzle_mapping.json'))
    c = json.load(f)
    def ame(x):
        map_ame = []
        t = x.split(',')
        for i in t:
            x = c[i]
            map_ame.append(x)
        return "|".join(map_ame)

    r = e.Element("dubizzlepropertyfeed")
    for i in data:
        z = 1

        listing = e.SubElement(r,"property")
        e.SubElement(listing,"status").text = c[i['status']]
        if c[i['subtype']] == "OF":
            e.SubElement(listing,"commercialtype").text = c[i['subtype']]
            e.SubElement(listing,"subtype").text = "CO"
        else:
            e.SubElement(listing,"commercialtype").text =""
            e.SubElement(listing,"subtype").text = c[i['subtype']]
        e.SubElement(listing,"type").text = c[i['type']]
        e.SubElement(listing,"city").text = c[i['city']]
        e.SubElement(listing,"locationtext").text = i['locationtext']
        e.SubElement(listing,"building").text = i['building']
        e.SubElement(listing,"refno").text = i['refno']
        e.SubElement(listing,"price").text = i['price']
        if i['type'] == "Sale":
            e.SubElement(listing,"totalclosingfee").text = ""
            e.SubElement(listing,"annualcommunityfee").text = ""
            e.SubElement(listing,"readyby").text = i['completion_date']
            if i['subtype'] == "Land":
                e.SubElement(listing,"freehold").text = i['tenure']
        if i['type'] == "Rent":
            e.SubElement(listing,"rentpriceterm").text = c[i['rentpriceterm']]
            e.SubElement(listing,"rentispaid").text = ""
            e.SubElement(listing,"agencyfee").text = ""
        e.SubElement(listing,"size").text = i['size']
        e.SubElement(listing,"sizeunits").text = "SqFt"
        if i['bedrooms'] == "ST":
            e.SubElement(listing,"bedrooms").text = "0"
        else:
            e.SubElement(listing,"bedrooms").text = i['bedrooms']
        e.SubElement(listing,"bathrooms").text = i['bathrooms']
        e.SubElement(listing,"title").text = i['title']
        e.SubElement(listing,"description").text = i['description']
        e.SubElement(listing,"privateamenities").text = ame(i['privateamenities'])
        e.SubElement(listing,"commercialamenities").text = ame(i['commercialamenities'])
        e.SubElement(listing,"contactnumber").text = '+971-54-9981998'
        e.SubElement(listing,"contactemail").text = 'bayut3@uhpae.com'
        e.SubElement(listing,"ImageUrl").text = i['photos']
        e.SubElement(listing,"developer").text = ""
        e.SubElement(listing,"furnished").text = i['furnished']
        e.SubElement(listing,"permit_number").text = i['permit_number']
        e.SubElement(listing,"view360").text = i['view360']
        e.SubElement(listing,"video_url").text = i['video_url']
        e.SubElement(listing,"lastupdated").text = str(datetime.now()+timedelta(hours=4))
        z = z + 1

    a = e.ElementTree(r)
    
    a.write("template/dubizzle.xml")
    print("added")
    





@handleproperties.route('/properties',methods = ['GET','POST'])
@login_required
def display_properties():
    if current_user.listing == False and current_user.sale == False:
        return abort(404)
    data = []
    if current_user.viewall == True and current_user.listing == True:
        for r in db.session.query(Properties).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['photos','title','description','plot','street','rentpriceterm','contactemail','contactnumber','furnished','privateamenities','commercialamenities','geopoint','permit_number','view360','video_url','completion_status','source','owner','tenant','parking','featured','offplan_status','tenure','expiry_date','deposit','commission','price_per_area','plot_size']: new.pop(k)
            if current_user.edit == True:
                if r.created_by == current_user.username or r.assign_to == current_user.username or current_user.is_admin == True:
                    edit_btn = '<a href="/edit_property/'+str(new['refno'])+'"><button  class="btn btn-primary si">Edit</button></a>'
                else:
                    edit_btn = ''
            else:
                edit_btn = ''
            new["edit"] ="<div style='display:flex;'>"+ edit_btn +'<button class="btn btn-danger si" data-toggle="modal" data-target="#viewModal" onclick="view_property('+"'"+new['refno']+"'"+')">View</button>'+'<button class="btn btn-warning si" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')">Notes</button>'+"</div>"
            data.append(new)
    elif current_user.viewall == False and current_user.listing == True:
        for r in db.session.query(Properties).filter(or_(Properties.created_by == current_user.username,Properties.assign_to == current_user.username)):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['photos','title','description','plot','street','rentpriceterm','contactemail','contactnumber','furnished','privateamenities','commercialamenities','geopoint','permit_number','view360','video_url','completion_status','source','owner','tenant','parking','featured','offplan_status','tenure','expiry_date','deposit','commission','price_per_area','plot_size']: new.pop(k)
            if current_user.edit == True:
                if r.created_by == current_user.username or r.assign_to == current_user.username:
                    edit_btn = '<a href="/edit_property/'+str(new['refno'])+'"><button  class="btn btn-primary si">Edit</button></a>'
                else:
                    edit_btn = ''
            else:
                edit_btn = ''
            new["edit"] ="<div style='display:flex;'>"+ edit_btn +'<button class="btn btn-danger si" data-toggle="modal" data-target="#viewModal" onclick="view_property('+"'"+new['refno']+"'"+')">View</button>'+'<button class="btn btn-warning si" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')">Notes</button>'+"</div>"
            data.append(new)
    elif current_user.sale == True and current_user.listing == False:
        for r in db.session.query(Properties).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['photos','title','description','plot','street','rentpriceterm','contactemail','contactnumber','furnished','privateamenities','commercialamenities','geopoint','unit','owner_contact','owner_name','owner_email','permit_number','view360','video_url','completion_status','source','owner','tenant','parking','featured','offplan_status','tenure','expiry_date','deposit','commission','price_per_area','plot_size']: new.pop(k)
            data.append(new)
    f = open('property_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    e = open('viewing.json')
    viewings = json.load(e)
    viewings = viewings["viewings"]
    return render_template('properties.html', viewings=viewings,data = data , columns = columns, user = current_user.username)

    
@handleproperties.route('/add_property/rent', methods = ['GET','POST'])
@login_required
def add_property_rent():  
    if current_user.listing == False:
        return abort(404)
    form = AddPropertyForm()
    if request.method == 'POST': 
        files_filenames = []
        status = form.status.data
        city = form.city.data
        type = "Rent"
        subtype = form.subtype.data
        title = form.title.data
        description = form.description.data
        unit = form.unit.data
        plot = form.plot.data
        street = form.street.data
        size = form.size.data
        plot_size = form.plot_size.data
        price = form.price.data
        rentpriceterm = form.rentpriceterm.data
        price_per_area = form.price_per_area.data
        bedrooms = form.bedrooms.data
        lastupdated = datetime.now()+timedelta(hours=4)
        w = open('abudhabi.json')
        file_data = json.load(w)
        locationtext = file_data[form.locationtext.data]
        furnished = form.furnished.data
        parking = form.parking.data
        featured = form.featured.data
        building = form.building.data
        privateamenities = ",".join(form.privateamenities.data)
        commercialamenities = ",".join(form.commercialamenities.data)
        geopoint = form.geopoint.data
        bathrooms = form.bathrooms.data
        permit_number = form.permit_number.data
        view360 = form.view360.data
        video_url = form.video_url.data 
        source = form.source.data
        owner = form.owner.data
        owner_name = form.owner_name.data
        owner_contact = form.owner_contact.data
        owner_email = form.owner_email.data
        tenant = form.tenant.data
        expiry_date = form.expiry_date.data
        assigned = form.assign_to.data
        assigned = assigned.split('|')
        assign_to = assigned[0]
        contactemail = assigned[2]
        contactnumber = assigned[1]
        portal = form.portal.data
        newproperty = Properties(lastupdated=lastupdated,portal=portal,geopoint=geopoint,owner_name=owner_name,owner_contact=owner_contact,owner_email=owner_email,contactemail=contactemail,contactnumber=contactnumber,featured=featured,parking=parking,tenant=tenant,expiry_date=expiry_date,price_per_area = price_per_area,plot_size = plot_size,status = status,city = city,type = type,subtype = subtype,title = title,description = description,size = size,price = price,rentpriceterm = rentpriceterm,bedrooms = bedrooms,locationtext = locationtext,furnished = furnished,building = building,privateamenities = privateamenities,bathrooms = bathrooms,permit_number = permit_number,view360 =  view360,video_url = video_url,source=source,owner=owner,assign_to=assign_to,unit=unit,plot=plot,street=street,commercialamenities=commercialamenities,created_by=current_user.username)
        db.session.add(newproperty)
        db.session.commit()
        db.session.refresh(newproperty)
        newproperty.refno = 'UNI-R-'+str(newproperty.id)
        try:
            for filex in form.photos.data:
                file_filename = secure_filename(filex.filename)
                directory = UPLOAD_FOLDER+'/UNI-R-'+str(newproperty.id)
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                filex.save(os.path.join(directory, file_filename))
                files_filenames.append('/static/uploads'+'/UNI-R-'+str(newproperty.id)+"/"+file_filename)
            newproperty.photos = '|'.join(files_filenames)
            db.session.commit()
        except:
            newproperty.photos = ''
            db.session.commit()
        logs(current_user.username,'UNI-R-'+str(newproperty.id),'Added')
        notes('UNI-R-' + str(newproperty.id))
        add_user_list(current_user.username, 'UNI-R-'+str(newproperty.id))
        #dubbizlexml()
        return redirect(url_for('handleproperties.display_properties'))
    return render_template('add_property.html', form=form, radio_enable = 'disabled', purpose = "rent",user = current_user.username)

@handleproperties.route('/add_property/sale', methods = ['GET','POST'])
@login_required
def add_property_sale():
    if current_user.listing == False:
        return abort(404) 
    form = AddPropertyForm()
    if request.method == 'POST': 
        files_filenames = []
        status = form.status.data
        city = form.city.data
        type = "Sale"
        subtype = form.subtype.data
        title = form.title.data
        description = form.description.data
        unit = form.unit.data
        plot = form.plot.data
        street = form.street.data
        size = form.size.data
        plot_size = form.plot_size.data
        price = form.price.data
        price_per_area = form.price_per_area.data
        bedrooms = form.bedrooms.data
        lastupdated = datetime.now()+timedelta(hours=4)
        w = open('abudhabi.json')
        file_data = json.load(w)
        locationtext = file_data[form.locationtext.data]
        furnished = form.furnished.data
        parking = form.parking.data
        featured = form.featured.data
        building = form.building.data
        privateamenities = ",".join(form.privateamenities.data)
        commercialamenities = ",".join(form.commercialamenities.data)
        geopoint = form.geopoint.data
        bathrooms = form.bathrooms.data
        permit_number = form.permit_number.data
        view360 = form.view360.data
        video_url = form.video_url.data 
        completion_status = form.completion_status.data
        source = form.source.data
        owner = form.owner.data
        owner_name = form.owner_name.data
        owner_contact = form.owner_contact.data
        owner_email = form.owner_email.data
        expiry_date = form.expiry_date.data
        tenure = form.tenure.data
        offplan_status = form.offplan_status.data 
        completion_date = form.completion_date.data 
        assigned = form.assign_to.data
        assigned = assigned.split('|')
        assign_to = assigned[0]
        contactemail = assigned[2]
        contactnumber = assigned[1]
        portal = form.portal.data
        newproperty = Properties(lastupdated=lastupdated,portal=portal, geopoint=geopoint,owner_name=owner_name,owner_contact=owner_contact,owner_email=owner_email,contactemail=contactemail,contactnumber=contactnumber,offplan_status = offplan_status, completion_date = completion_date,tenure=tenure,featured=featured,parking=parking,expiry_date=expiry_date,price_per_area = price_per_area,plot_size = plot_size,status = status,city = city,type = type,subtype = subtype,title = title,description = description,size = size,price = price,bedrooms = bedrooms,locationtext = locationtext,furnished = furnished,building = building,privateamenities = privateamenities,bathrooms = bathrooms,permit_number = permit_number,view360 =  view360, video_url = video_url, completion_status = completion_status,source=source,owner=owner,assign_to=assign_to,unit=unit,plot=plot,street=street,commercialamenities=commercialamenities,created_by=current_user.username)
        db.session.add(newproperty)
        db.session.commit()
        db.session.refresh(newproperty)
        newproperty.refno = 'UNI-S-'+str(newproperty.id)
        try:
            for filex in form.photos.data:
                file_filename = secure_filename(filex.filename)
                directory = UPLOAD_FOLDER+'/UNI-S-'+str(newproperty.id)
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                filex.save(os.path.join(directory, file_filename))
                files_filenames.append('/static/uploads'+'/UNI-S-'+str(newproperty.id)+"/"+file_filename)
            newproperty.photos = '|'.join(files_filenames)
            db.session.commit()
        except:
             newproperty.photos = ''
             db.session.commit()
        logs(current_user.username,'UNI-S-'+str(newproperty.id),'Added')
        notes('UNI-S-' + str(newproperty.id))
        add_user_list(current_user.username, 'UNI-S-'+str(newproperty.id))
        return redirect(url_for('handleproperties.display_properties'))
    return render_template('add_property.html', form=form, radio_enable = 'disabled', purpose = "sale", user=current_user.username)



@handleproperties.route('/edit_property/<variable>', methods = ['GET','POST'])
@login_required
def edit_property(variable): 
    db.session.rollback()
    if current_user.listing == False or current_user.edit == False:
        return abort(404)
    if "R" in variable:
        category = "rent"
    else:
        category = "sale"
    edit = db.session.query(Properties).filter_by(refno = variable).first()

    form = AddPropertyForm(obj = edit)
    w = open('abudhabi.json')
    mydict = json.load(w)
    new = form.locationtext.data
    form.locationtext.data = list(mydict.keys())[list(mydict.values()).index(edit.locationtext)]
    old_photos = edit.photos
    if request.method == 'POST':
        form.populate_obj(edit)
        edit.privateamenities = ",".join(form.privateamenities.data)
        edit.commercialamenities = ",".join(form.commercialamenities.data)
        assigned = form.assign_to.data
        assigned = assigned.split('|')
        edit.assign_to = assigned[0]
        edit.contactemail = assigned[2]
        edit.contactnumber = assigned[1]
        w = open('abudhabi.json')
        file_data = json.load(w)
        edit.locationtext = file_data[new]
        files_filenames = []
        delete = form.new_files.data
        if delete == '1':
            files = glob.glob(UPLOAD_FOLDER+'/'+edit.refno+'/*')
            for f in files:
                os.remove(f)
        for filex in form.photos.data:
            file_filename = secure_filename(filex.filename)
            if file_filename == '':
                break
            filex.save(os.path.join(UPLOAD_FOLDER+'/'+edit.refno, file_filename))
            files_filenames.append('/static/uploads'+'/'+edit.refno+'/'+file_filename)
        if delete == '0':
            z = '|'.join(files_filenames)    
            edit.photos = old_photos+'|'+z
        else:
            edit.photos = '|'.join(files_filenames)
        db.session.commit()
        logs(current_user.username,edit.refno,'Edited')
        return redirect(url_for('handleproperties.display_properties'))
    if edit.privateamenities != None:
        form.privateamenities.data = edit.privateamenities.split(',')
    if edit.commercialamenities != None:
        form.commercialamenities.data = edit.commercialamenities.split(',')
    return render_template('add_property.html', form=form, radio_enable = 'enabled',community=edit.locationtext, building = edit.building, purpose=category, assign=edit.assign_to,user=current_user.username)


@handleproperties.route('/community/<location>',methods = ['GET','POST'])
@login_required
def community(location):
    a = location
    f = open('sublocation.json')
    file_data = json.load(f)
    a = str(int(a))
    try:
        locs = file_data[a]
    except:
        locs = {"9998":"None"}
    locs = list(locs.values())
    locations = []
    for i in locs:
        locations.append((i,i))
    return jsonify({'locations':locations})

@handleproperties.route('/property/<location>',methods = ['GET','POST'])
@login_required
def propertyloc(location):
    a = location.replace('%20', " ")
    f = open('sublocation.json')
    file_data = json.load(f)
    w = open('contacts.json')
    x = json.load(w)
    x = x["ABD"]
    for key, value in x[0].items():
        if a == value:
            a = key
    a = str(int(a))
    try:
        locs = file_data[a]
    except:
        locs = {"9998":"None"}
    locs = list(locs.values())
    locations = []
    for i in locs:
        locations.append((i,i))
    return jsonify({'locations':locations})



@handleproperties.route('/date',methods = ['GET','POST'])
@login_required
def date():
    with open('map_listing.json','r+') as file:
        ls = json.load(file)
        ls = ls["map_listing"]
    with open("all_listing2.csv", "r") as f:
        reader = csv.reader(f, delimiter=",")
        listings = []
        for row in reader:
            a = row
            listings.append(a[1:])
        for i in listings[1:]:
            try:    
                ls_value = ls[i[0]]
                o = db.session.query(Properties).filter_by(refno=ls_value).first()
                d = datetime.strptime(i[2][0:6]+i[2][8:]+" 00:00:00", '%d/%m/%y %H:%M:%S')
                o.lastupdated = d
                db.session.commit()
                print(o.refno)
            except:
                pass
    return "ok"

@handleproperties.route('/reassign',methods = ['GET','POST'])
@login_required
def reassign():
    o = db.session.query(Properties).filter_by(refno="UNI-S-448").first()
    o = o.lastupdated
    for i in db.session.query(Properties).filter_by(locationtext="Al Raha Beach").all():
        try:
            print(i.lastupdated.date())
        except:
            i.lastupdated = o
            db.session.commit()
            m = i.lastupdated.month
            y = i.lastupdated.year
            if int(y) <= 2020:
                i.assign_to = "maria" 
                db.session.commit()
            elif int(y) > 2020 and int(m) <= 8:
                i.assign_to = "maria" 
                db.session.commit()
    for i in db.session.query(Properties).filter_by(locationtext="Al Reem Island").all():
        try:
            print(i.lastupdated.date())
        except:
            i.lastupdated = o
            db.session.commit()
            m = i.lastupdated.month
            y = i.lastupdated.year
            if int(y) <= 2020:
                i.assign_to = "islam_roushdy" 
                db.session.commit()
            elif int(y) > 2020 and int(m) <= 8:
                i.assign_to = "islam_roushdy" 
                db.session.commit()
    return "ok"

@handleproperties.route('/reassign2',methods = ['GET','POST'])
@login_required
def reassign2():
    z = datetime.strptime("21-04-03 00:00:00", '%y-%m-%d %H:%M:%S')
    for i in db.session.query(Properties).all():
        conn = sqlite3.connect('test2.db')
        cur = conn.cursor()
        teststr = "SELECT lastupdated FROM Properties WHERE refno='{}'".format(i.refno)
        cur.execute(teststr)
        rows = cur.fetchone()
        try:
            date_time_obj = datetime.strptime(rows[0][2:].split('.')[0], '%y-%m-%d %H:%M:%S')
        except: 
            date_time_obj = z
        i.lastupdated = date_time_obj
        db.session.commit()
    return  "posla"

