from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import exc
from sqlalchemy.sql.elements import Null
from models import Properties, Contacts, User
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
import requests
import json
import re
import sqlite3
import os
import csv
import time

FILE_UPLOADS = os.getcwd() + "/static/imports/uploads"

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
                if r.created_by == current_user.username or r.assign_to == current_user.username or current_user.is_admin == True or current_user.team_members == "LA":
                    edit_btn = '<a href="/edit_property/'+str(new['refno'])+'"><img style="width:10%;" src="/static/images/edit.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">Edit</small></a>'
                else:
                    edit_btn = ''
            else:
                edit_btn = ''
            if new["assign_to"] == current_user.username or new["created_by"] == current_user.username or current_user.is_admin == True or current_user.team_members == "LA" or current_user.listing == True:
                pass
            else:
                new["owner_contact"] = "*"
            if new["portal"] == "0":
                website = "https://uhpae.com/communities/"+new["locationtext"].replace(' ', '-')+"/"+new["building"].replace(' ', '-')+"/"+new["refno"].replace(' ', '-')
                new["portal"] = '<a href='+website+'><img src="/static/images/logo_blue.png" alt="HTML tutorial" style="width:21px;"></a>'
            else:
                new["portal"] = "Not Promoted"
            if new['property_finder'] != 'None':
                link = new['property_finder'].split('|')
                if new["portal"] == "Not Promoted":
                    new["portal"] = '<a href='+link[-1]+'><img src="/static/images/pf_logo.png" alt="HTML tutorial" style="width:21px;"></a>'
                else:
                    new["portal"] += '<a href='+link[-1]+'><img src="/static/images/pf_logo.png" alt="HTML tutorial" style="width:21px; margin-left:15px"></a>'                
            else:
                pass
            view_btn = '<a data-toggle="modal" data-target="#viewModal" onclick="view_property('+"'"+new['refno']+"'"+')"><img style="width:10%;" src="/static/images/eye.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">View</small></a>'
            note_btn = '<a style="border-bottom: 0.5px solid black;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')"><img style="width:10%;" src="/static/images/notes.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">Notes</small></a>'
            startpromotion = '<a onclick="startpromotion('+"'"+new['refno']+"'"+')"><img style="width:10%;" src="/static/images/global.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">Website</small></a>'
            stoppromotion = '<a style="border-bottom: 0.5px solid black;" onclick="stoppromotion('+"'"+new['refno']+"'"+')"><img style="width:10%;" src="/static/images/cross.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">Remove</small></a>'
            if new['property_finder'] == 'None':
                startpf = '<a onclick="propertyfinder03('+"'"+new['refno']+"'"+')"><img style="width:13%;" src="/static/images/pf_logo.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">PF</small></a>'
                stoppf = ''
            else:
                startpf = '<a onclick="update_that_property('+"'"+new['refno']+"'"+')"><img style="width:13%;" src="/static/images/pf_logo.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">Update</small></a>'
                stoppf = '<a onclick="stoppf('+"'"+new['refno']+"'"+')"><img style="width:10%;" src="/static/images/cross.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">Remove</small></a>'
            new["edit"] ="<div class='dropdown'><button class='dropbtn' style='margin-top: 1px; font-size: 17px; width: 90px'><img style='width:12px; float: left; filter: invert(); margin-right: 1px; margin-left: 3px; margin-top: 7%;' src='/static/images/more.png'/><span>Action</button><div class='dropdown-content'>"+edit_btn+view_btn+note_btn+startpromotion+stoppromotion+startpf+stoppf+"</div></div>"
            data.append(new)
    elif current_user.viewall == False and current_user.listing == True:
        for r in db.session.query(Properties).filter(or_(Properties.created_by == current_user.username,Properties.assign_to == current_user.username)):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['photos','title','description','plot','street','rentpriceterm','contactemail','contactnumber','furnished','privateamenities','commercialamenities','geopoint','permit_number','view360','video_url','completion_status','source','owner','tenant','parking','featured','offplan_status','tenure','expiry_date','deposit','commission','price_per_area','plot_size']: new.pop(k)
            if current_user.edit == True:
                if r.created_by == current_user.username or r.assign_to == current_user.username:
                    edit_btn = '<a href="/edit_property/'+str(new['refno'])+'">Edit</a>'
                else:
                    edit_btn = ''
            else:
                edit_btn = ''
            if new["portal"] == "0":
                website = "https://uhpae.com/communities/"+new["locationtext"].replace(' ', '-')+"/"+new["building"].replace(' ', '-')+"/"+new["refno"].replace(' ', '-')
                new["portal"] = '<a href='+website+'><img src="/static/images/logo_blue.png" alt="HTML tutorial" style="width:21px;"></a>'
            else:
                new["portal"] = "Not Promoted"
            if new['property_finder'] != 'None':
                link = new['property_finder'].split('|')
                if new["portal"] == "Not Promoted":
                    new["portal"] = '<a href='+link[-1]+'><img src="/static/images/pf_logo.png" alt="HTML tutorial" style="width:21px;"></a>'
                else:
                    new["portal"] += '<a href='+link[-1]+'><img src="/static/images/pf_logo.png" alt="HTML tutorial" style="width:21px; margin-left:15px"></a>'                
            else:
                pass
            view_btn = '<a data-toggle="modal" data-target="#viewModal" onclick="view_property('+"'"+new['refno']+"'"+')">View</a>'
            note_btn = '<a data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')">Notes</a>'
            startpromotion = '<a onclick="startpromotion('+"'"+new['refno']+"'"+')"><img style="width:10%;" src="/static/images/global.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">Website</small><</a>'
            stoppromotion = '<a style="border-bottom: 0.5px solid black;" onclick="stoppromotion('+"'"+new['refno']+"'"+')"><img style="width:10%;" src="/static/images/cross.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">Remove</small><</a>'
            if new['property_finder'] == 'None':
                startpf = '<a onclick="propertyfinder03('+"'"+new['refno']+"'"+')"><img style="width:13%;" src="/static/images/pf_logo.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">PF</small></a>'
                stoppf = ''
            else:
                startpf = '<a onclick="update_that_property('+"'"+new['refno']+"'"+')"><img style="width:13%;" src="/static/images/pf_logo.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">Update</small></a>'
                stoppf = '<a onclick="stoppf('+"'"+new['refno']+"'"+')"><img style="width:10%;" src="/static/images/cross.png"/><span><small style="margin-left: 7px; font-size: 15px; color: black">Remove</small></a>'
            new["edit"] ="<div class='dropdown'><button class='dropbtn' style='margin-top: 1px; font-size: 17px; width: 90px'><img style='width:12px; float: left; filter: invert(); margin-right: 1px; margin-left: 3px; margin-top: 7%;' src='/static/images/more.png'/><span>Action</button><div class='dropdown-content'>"+edit_btn+view_btn+note_btn+startpromotion+stoppromotion+startpf+stoppf+"</div></div>"
            data.append(new)
    elif current_user.team_members == "QC" and current_user.listing == False:
        for r in db.session.query(Properties).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['photos','title','description','plot','street','rentpriceterm','contactemail','contactnumber','furnished','privateamenities','commercialamenities','geopoint','unit','permit_number','view360','video_url','completion_status','source','owner','tenant','parking','featured','offplan_status','tenure','expiry_date','deposit','commission','price_per_area','plot_size']: new.pop(k)
            new["edit"] = '<button class="btn btn-warning si" style="color:white;" data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')">Notes</button>'+"</div>"
            data.append(new)
    elif current_user.sale == True and current_user.listing == False:
        for r in db.session.query(Properties).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['photos','title','description','plot','street','rentpriceterm','contactemail','contactnumber','furnished','privateamenities','commercialamenities','geopoint','unit','owner_contact','owner_name','owner_email','permit_number','view360','video_url','completion_status','source','owner','tenant','parking','featured','offplan_status','tenure','expiry_date','deposit','commission','price_per_area','plot_size']: new.pop(k)
            if new["portal"] == "0":
                website = "https://uhpae.com/communities/"+new["locationtext"].replace(' ', '-')+"/"+new["building"].replace(' ', '-')+"/"+new["refno"].replace(' ', '-')
                new["portal"] = '<a href='+website+'><img src="/static/images/logo_blue.png" alt="HTML tutorial" style="width:21px;"></a>'
            else:
                new["portal"] = "Not Promoted"
            if new['property_finder'] != 'None':
                link = new['property_finder'].split('|')
                if new["portal"] == "Not Promoted":
                    new["portal"] = '<a href='+link[-1]+'><img src="/static/images/pf_logo.png" alt="HTML tutorial" style="width:21px;"></a>'
                else:
                    new["portal"] += '<a href='+link[-1]+'><img src="/static/images/pf_logo.png" alt="HTML tutorial" style="width:21px; margin-left:15px"></a>'                
            else:
                pass
            view_btn = '<a data-toggle="modal" data-target="#viewModal" onclick="view_property('+"'"+new['refno']+"'"+')">View</a>'
            note_btn = '<a data-toggle="modal" data-target="#notesModal" onclick="view_note('+"'"+new['refno']+"'"+')">Notes</a>'
            new["edit"] ="<div class='dropdown'><button class='dropbtn' style='margin-top: 1px; font-size: 17px; width: 90px'><img style='width:12px; float: left; filter: invert(); margin-right: 1px; margin-left: 3px; margin-top: 7%;' src='/static/images/more.png'/><span>Action</button><div class='dropdown-content'>"+view_btn+note_btn+"</div></div>"
            data.append(new)
    f = open('property_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    e = open('viewing.json')
    viewings = json.load(e)
    viewings = viewings["viewings"]
    all_listing_users = db.session.query(User).filter_by(listing = True).all()
    return render_template('properties.html', viewings=viewings,data = data , columns = columns, user = current_user.username, all_listing_users = all_listing_users)

    
@handleproperties.route('/add_property/rent', methods = ['GET','POST'])
@login_required
def add_property_rent():  
    if current_user.listing == False:
        return abort(404)
    form = AddPropertyForm()
    if request.method == 'POST': 
        files_filenames = []
        files01_filenames = []
        files02_filenames = []
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
        created_at = datetime.now()+timedelta(hours=4)
        w = open('abudhabi.json')
        file_data = json.load(w)
        locationtext = file_data[form.locationtext.data]
        furnished = form.furnished.data
        parking = form.parking.data
        featured = form.featured.data
        building = form.building.data
        privateamenities = ",".join(form.privateamenities.data)
        commercialamenities = ",".join(form.commercialamenities.data)
        completion_status = form.completion_status.data
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
        view = form.view.data
        cheques = form.cheques.data
        newproperty = Properties(created_at=created_at,lastupdated=lastupdated,portal=portal,geopoint=geopoint,owner_name=owner_name,owner_contact=owner_contact,owner_email=owner_email,contactemail=contactemail,completion_status = completion_status,contactnumber=contactnumber,featured=featured,parking=parking,tenant=tenant,expiry_date=expiry_date,price_per_area = price_per_area,plot_size = plot_size,status = status,city = city,type = type,subtype = subtype,title = title,description = description,size = size,price = price,rentpriceterm = rentpriceterm,bedrooms = bedrooms,locationtext = locationtext,furnished = furnished,building = building,privateamenities = privateamenities,bathrooms = bathrooms,permit_number = permit_number,view360 =  view360,view=view,video_url = video_url,source=source,owner=owner,assign_to=assign_to,unit=unit,plot=plot,street=street,commercialamenities=commercialamenities,cheques=cheques,created_by=current_user.username)
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
        try:
            for filex in form.floorplan.data:
                file_filename = secure_filename(filex.filename)
                directory = UPLOAD_FOLDER+'/UNI-R-'+str(newproperty.id)+'/floorplan'
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                filex.save(os.path.join(directory, file_filename))
                files01_filenames.append('/static/uploads'+'/UNI-R-'+str(newproperty.id)+"/floorplan/"+file_filename)
            newproperty.floorplan = '|'.join(files01_filenames)
            db.session.commit()
        except:
             newproperty.floorplan = ''
             db.session.commit()
        try:
            for filex in form.masterplan.data:
                file_filename = secure_filename(filex.filename)
                directory = UPLOAD_FOLDER+'/UNI-R-'+str(newproperty.id)+'/masterplan'
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                filex.save(os.path.join(directory, file_filename))
                files02_filenames.append('/static/uploads'+'/UNI-R-'+str(newproperty.id)+"/masterplan/"+file_filename)
            newproperty.masterplan = '|'.join(files02_filenames)
            db.session.commit()
        except:
             newproperty.masterplan = ''
             db.session.commit()
        logs(current_user.username,'UNI-R-'+str(newproperty.id),'Added')
        notes('UNI-R-' + str(newproperty.id))
        add_user_list(current_user.username, 'UNI-R-'+str(newproperty.id))
        #dubbizlexml()
        return redirect(url_for('handleproperties.display_properties'))
    return render_template('add_property.html', form=form, radio_enable = 'disabled', purpose = "rent",user = current_user.username, old_photos = "", variable="", old_floorplan = "", old_masterplan = "")

@handleproperties.route('/add_property/sale', methods = ['GET','POST'])
@login_required
def add_property_sale():
    if current_user.listing == False:
        return abort(404) 
    form = AddPropertyForm()
    if request.method == 'POST': 
        files_filenames = []
        files01_filenames = []
        files02_filenames = []
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
        created_at = datetime.now()+timedelta(hours=4)
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
        view = form.view.data
        newproperty = Properties(created_at=created_at,lastupdated=lastupdated,portal=portal, geopoint=geopoint,owner_name=owner_name,owner_contact=owner_contact,owner_email=owner_email,contactemail=contactemail,contactnumber=contactnumber,offplan_status = offplan_status, completion_date = completion_date,tenure=tenure,featured=featured,parking=parking,expiry_date=expiry_date,price_per_area = price_per_area,plot_size = plot_size,status = status,city = city,type = type,subtype = subtype,title = title,description = description,size = size,price = price,bedrooms = bedrooms,locationtext = locationtext,furnished = furnished,building = building,privateamenities = privateamenities,bathrooms = bathrooms,permit_number = permit_number,view360 =  view360,view = view, video_url = video_url, completion_status = completion_status,source=source,owner=owner,assign_to=assign_to,unit=unit,plot=plot,street=street,commercialamenities=commercialamenities,created_by=current_user.username)
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
        try:
            for filex in form.floorplan.data:
                file_filename = secure_filename(filex.filename)
                directory = UPLOAD_FOLDER+'/UNI-S-'+str(newproperty.id)+'/floorplan'
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                filex.save(os.path.join(directory, file_filename))
                files01_filenames.append('/static/uploads'+'/UNI-S-'+str(newproperty.id)+"/floorplan/"+file_filename)
            newproperty.floorplan = '|'.join(files01_filenames)
            db.session.commit()
        except:
             newproperty.floorplan = ''
             db.session.commit()
        try:
            for filex in form.masterplan.data:
                file_filename = secure_filename(filex.filename)
                directory = UPLOAD_FOLDER+'/UNI-S-'+str(newproperty.id)+'/masterplan'
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                filex.save(os.path.join(directory, file_filename))
                files02_filenames.append('/static/uploads'+'/UNI-S-'+str(newproperty.id)+"/masterplan/"+file_filename)
            newproperty.masterplan = '|'.join(files02_filenames)
            db.session.commit()
        except:
             newproperty.masterplan = ''
             db.session.commit()
        logs(current_user.username,'UNI-S-'+str(newproperty.id),'Added')
        notes('UNI-S-' + str(newproperty.id))
        add_user_list(current_user.username, 'UNI-S-'+str(newproperty.id))
        return redirect(url_for('handleproperties.display_properties'))
    return render_template('add_property.html', form=form, radio_enable = 'disabled', purpose = "sale", user=current_user.username, old_photos = "", variable="", old_floorplan = "", old_masterplan = "")



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
    old_floorplan = edit.floorplan
    old_masterplan = edit.masterplan
    if request.method == 'POST':
        form.populate_obj(edit)
        edit.privateamenities = ",".join(form.privateamenities.data)
        edit.commercialamenities = ",".join(form.commercialamenities.data)
        assigned = form.assign_to.data
        assigned = assigned.split('|')
        edit.assign_to = assigned[0]
        edit.contactemail = assigned[2]
        edit.contactnumber = assigned[1]
        edit.lastupdated = datetime.now()+timedelta(hours=4)
        w = open('abudhabi.json')
        file_data = json.load(w)
        edit.locationtext = file_data[new]
        files_filenames = []
        files_filenames01 = []
        files_filenames02 = []
        delete = form.new_files.data
        delete1 = form.new_files01.data
        delete2 = form.new_files02.data
        if not os.path.isdir(UPLOAD_FOLDER+'/'+edit.refno): 
            os.mkdir(UPLOAD_FOLDER+'/'+edit.refno)
        if not os.path.isdir(UPLOAD_FOLDER+'/'+edit.refno+'/floorplan'): 
            os.mkdir(UPLOAD_FOLDER+'/'+edit.refno+'/floorplan')
        if not os.path.isdir(UPLOAD_FOLDER+'/'+edit.refno+'/masterplan'): 
            os.mkdir(UPLOAD_FOLDER+'/'+edit.refno+'/masterplan')




        if delete == '1': # for deleting purposes
            files = glob.glob(UPLOAD_FOLDER+'/'+edit.refno+'/*')
            for f in files: # simply deleting all the photos in the current directory
                os.remove(f)
        for filex in form.photos.data: # these are the new photos uploaded 
            file_filename = secure_filename(filex.filename) # checking for valid file name 
            if file_filename == '': 
                break # gawddamn yahan pe tou scene hi khatam hoo geya 
            filex.save(os.path.join(UPLOAD_FOLDER+'/'+edit.refno, file_filename)) # directory mei saved 
            files_filenames.append('/static/uploads'+'/'+edit.refno+'/'+file_filename) # new pictures are now saved in an array 
        if delete == '0':
            z = '|'.join(files_filenames)    # new pictures saved in the "|" format
            if old_photos == None and file_filename != '':
                edit.photos = z # only new pictures being added 
            elif file_filename != '':
                edit.photos = old_photos+'|'+z # new pictures added with the new ones here 
            else:
                edit.photos = old_photos
        else:
            pass




        
        if delete1 == '1': # for deleting purposes
            files = glob.glob(UPLOAD_FOLDER+'/'+edit.refno+'/floorplan/*')
            for f in files: # simply deleting all the photos in the current directory
                os.remove(f)
        for filex in form.floorplan.data: # these are the new photos uploaded 
            file_filename01 = secure_filename(filex.filename) # checking for valid file name 
            if file_filename01 == '': 
                break # gawddamn yahan pe tou scene hi khatam hoo geya 
            filex.save(os.path.join(UPLOAD_FOLDER+'/'+edit.refno+'/floorplan', file_filename01)) # directory mei saved 
            files_filenames01.append('/static/uploads'+'/'+edit.refno+'/floorplan/'+file_filename01) # new pictures are now saved in an array 
        if delete1 == '0':
            z = '|'.join(files_filenames01)    #new pictures saved in the "|" format
            if old_floorplan == None and file_filename01 != '':
                edit.floorplan = z # only new pictures being added 
            elif file_filename01 != '':
                edit.floorplan = old_floorplan+'|'+z # new pictures added with the new ones here 
            else:
                edit.floorplan = old_floorplan
        else:
            if file_filename01 != '':
                edit.floorplan = '|'.join(files_filenames01)
            else:
                edit.floorplan = None




        if delete2 == '1': # for deleting purposes
            files = glob.glob(UPLOAD_FOLDER+'/'+edit.refno+'/masterplan/*')
            for f in files: # simply deleting all the photos in the current directory
                os.remove(f)
        for filex in form.masterplan.data: # these are the new photos uploaded 
            file_filename02 = secure_filename(filex.filename) # checking for valid file name 
            if file_filename02 == '': 
                break # gawddamn yahan pe tou scene hi khatam hoo geya 
            filex.save(os.path.join(UPLOAD_FOLDER+'/'+edit.refno+'/masterplan', file_filename02)) # directory mei saved 
            files_filenames02.append('/static/uploads'+'/'+edit.refno+'/masterplan/'+file_filename02) # new pictures are now saved in an array 
        if delete2 == '0':
            z = '|'.join(files_filenames02)    # new pictures saved in the "|" format
            if old_masterplan == None and file_filename02 != '': 
                edit.masterplan = z # only new pictures being added 
            elif file_filename02 != '':
                edit.masterplan = old_masterplan+'|'+z # new pictures added with the new ones here 
            else:
                edit.masterplan = old_masterplan
        else:
            if file_filename02 != '':
                edit.masterplan = '|'.join(files_filenames02)
            else:
                edit.masterplan = None



        db.session.commit()
        logs(current_user.username,edit.refno,'Edited')
        return (redirect(url_for('handleproperties.display_properties')))
    if edit.privateamenities != None:
        form.privateamenities.data = edit.privateamenities.split(',')
    if edit.commercialamenities != None:
        form.commercialamenities.data = edit.commercialamenities.split(',')
    return render_template('add_property.html', form=form, radio_enable = 'enabled',community=edit.locationtext, building = edit.building, purpose=category, assign=edit.assign_to,user=current_user.username, old_photos=old_photos, variable=variable, old_floorplan = old_floorplan, old_masterplan = old_masterplan)


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
    for i in db.session.query(Properties).filter_by(building="Hidd Al Saadiyat").all():
        i.assign_to = "april" 
        i.created_by = "april" 
        db.session.commit()
    return "ok"

@handleproperties.route('/reassign_property/<personA>/<personB>')
@login_required
def reassign_properties(personA,personB):
    all_leads = db.session.query(Properties).filter(or_(Properties.created_by == personA,Properties.assign_to == personA))
    for i in all_leads:
        i.assign_to = personB
        i.created_by = personB
        db.session.commit()
    return "ok"

@handleproperties.route('/notescreation')
@login_required
def notescreation():
    all_leads = db.session.query(Properties).filter(and_(Properties.status == "Pending", Properties.created_by == "engy",Properties.building == "Lea", Properties.assign_to == "suha", Properties.locationtext == "Yas Island"))
    for i in all_leads:
        notes(str(i.refno))
    return "ok"



@handleproperties.route('/reassign69_property/<personA>/<personB>') #lesssgooo
@login_required
def reassign69_properties(personA,personB):
    all_leads = db.session.query(Properties).filter(and_(Properties.assign_to == personA,Properties.status == "Available",Properties.locationtext == "Saadiyat Island", Properties.building == "Mamsha Al Saadiyat"))
    for i in all_leads:
        i.assign_to = personB
        db.session.commit()
    return "ok"

@handleproperties.route('/reassign72_property/<personA>') #lesssgooo
@login_required
def reassign72_properties(personA):
    all_leads = db.session.query(Properties).filter(and_(Properties.bedrooms == "4",Properties.status == "Rented",Properties.locationtext == "Yas Island", Properties.building == "Yas Acres"))
    for i in all_leads:
        i.assign_to = personA
        db.session.commit()
    return "ok"


@handleproperties.route('/reassign95_property/<personA>') #lesssgooo
@login_required
def reassign95_properties(personA):
    all_leads = db.session.query(Properties).filter(or_(Properties.refno == "UNI-S-2723", Properties.refno == "UNI-S-3137", Properties.refno == "UNI-S-3657"))
    for i in all_leads:
        i.assign_to = personA
        db.session.commit()
    return "ok"


@handleproperties.route('/startpromotion/<refnum>') #lesssgooo
@login_required
def startpromotion(refnum):
    all_leads = db.session.query(Properties).filter(Properties.refno == refnum)
    for i in all_leads:
        i.portal = "0"
        db.session.commit()
    return jsonify(success=True)

@handleproperties.route('/removepromotion/<refnum>') #lesssgooo
@login_required
def removepromotion(refnum):
    all_leads = db.session.query(Properties).filter(Properties.refno == refnum)
    for i in all_leads:
        i.portal = "1"
        db.session.commit()
    return jsonify(success=True)

@handleproperties.route('/deleteimages/<element>/<refnum>') #lesssgooo
@login_required
def deleteimage(element, refnum):
    all_leads = db.session.query(Properties).filter(Properties.refno == refnum)
    files = sorted(glob.glob(UPLOAD_FOLDER+'/'+refnum+'/*'))
    print(element)
    yo = element.split(",")
    for i in all_leads:
        x=i.photos.split("|")
    w=0
    for i in yo:
        for f in files:
            if x[int(i)-w][-15:] == f[-15:]:
                os.remove(f)
                x.__delitem__(int(i)-w)
                w+=1
                print(w)
                break
            else:
                continue
    z="|".join(x)
    for i in all_leads:
        if z != "":
            i.photos = z
        else:
            i.photos = None
    db.session.commit()
    return jsonify(success=True)


@handleproperties.route('/debugdaddy') #lesssgooo
@login_required
def debugdaddy():
    all_leads = db.session.query(Properties).filter(or_(Properties.refno == "UNI-S-3969", Properties.refno == "UNI-S-4006"))
    for i in all_leads:
        i.price_per_area = 0.0
        db.session.commit()
    return "ok"



@handleproperties.route('/reassign2',methods = ['GET','POST'])
@login_required
def reassign2():
    for i in db.session.query(Properties).filter_by(building = "West Yas"):
        d = i.lastupdated
        z = d.date().year
        if z < 2022:
            i.assign_to = "maria" 
            i.created_by = "maria" 
            db.session.commit()
    return  "posla"


@handleproperties.route('/delete_all_properties',methods = ['GET','POST'])
@login_required
def deleteallleads():
    r = "UNI-R-"
    s = "UNI-S-"
    l = [r+'4393', r+'4394', r+'4395']
    for i in l:
        delete = db.session.query(Properties).filter_by(refno=i).first()
        if delete:
            db.session.delete(delete)
            db.session.commit()
    return "ok"

@handleproperties.route('/no_portals',methods = ['GET','POST'])
@login_required
def rmportals():
    l = db.session.query(Properties).all()
    for i in l:
        i.portal = 1
        db.session.commit()
    return "ok"

@handleproperties.route('/cleaning_photos',methods = ['GET','POST'])
@login_required
def cleaning_photos():
    l = db.session.query(Properties).all()
    for i in l:
        a=i.photos
        if a != None:
            q=a.split("|")
            h=0
            for w in range(len(q)):
                if q[w-h]=="":
                    q.__delitem__(w-h)
                    h+=1
                else:
                    continue
            if q == []:
                i.photos = None
            else:
                i.photos='|'.join(q)
        else:
            continue
    db.session.commit()
    return "ok"


@handleproperties.route('/cleaning_photos_hardcore/<refno>',methods = ['GET','POST'])
@login_required
def cleaning_photos_hardcore(refno):
    l = db.session.query(Properties).filter_by(refno=refno).first()
    l.photos = None
    db.session.commit()
    return "ok"

@handleproperties.route('/pf_uhp',methods = ['GET','POST'])
@login_required
def pf_uhp():
    l = db.session.query(Properties)
    for m in l:
        if m.property_finder!=None:
            m.portal = 0
        else:
            pass
    db.session.commit()
    return "ok"

@handleproperties.route('/uploadlisting',methods = ['GET','POST'])
@login_required
def uploadFiles():
    uploaded_file = request.files['file']
    filepath = os.path.join(FILE_UPLOADS, uploaded_file.filename)
    uploaded_file.save(filepath)
    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            print(row[11])
            if line_count == 0:
                print("Lesssgooo with count = 0")
                line_count += 1
            else:
                print("Now count is greater than 0")
                num_check = row[13].replace(" ", "").replace("+","")[3:]
                i = db.session.query(Contacts).filter(Contacts.number.endswith(num_check)).first()
                if (i):
                    owner = i.refno
                    row[11] = i.first_name + i.last_name
                    row[12] = i.email
                    row[13] = row[13].replace(" ", "").replace("+","")
                else: 
                    first_name = row[11].split(" ")[0]
                    if len(row[11].split(" ")) > 1: 
                        last_name = ' '.join(row[11].split(" ")[1:])
                    else: 
                        last_name = ''

                    number = row[13]
                    email = row[12]
                    newcontact = Contacts(first_name=first_name, last_name=last_name ,number=number,email=email, assign_to=current_user.username)
                    db.session.add(newcontact)
                    db.session.commit()
                    db.session.refresh(newcontact)
                    newcontact.refno = 'UNI-O-'+str(newcontact.id)
                    db.session.commit()
                    owner = 'UNI-O-'+str(newcontact.id)
                print("Property Checking")    
                fa = db.session.query(Properties).filter(and_(Properties.locationtext == row[4], Properties.building == row[5], Properties.unit == row[1])).first()
                if not (fa):
                    status = row[0]
                    unit = row[1]
                    subtype = row[2]
                    city = row[3]
                    locationtext = row[4]
                    building = row[5]
                    bedrooms = row[6]
                    #size = row[7]
                    price = row[8]
                    description = row[9]
                    assign_to = row[10]
                    owner_name = row[11]
                    owner_email = row[12] 
                    owner_contact = row[13]
                    plot = row[14]
                    bathrooms = row[15]
                    street = row[16]
                    source = row[17]
                    furnished = row[18]
                    #plot_size = row[19]
                    title = row[20]
                    commission = row[21]
                    deposit = row[22]
                    #price_per_area = row[23]
                    created_by = row[24]
                    completion_status = row[25]
                    #expiry_date = ''
                    parking = row[27]
                    type = row[28]
                    lastupdated = datetime.now()+timedelta(hours=4)
                    created_at = datetime.now()+timedelta(hours=4)
                    newproperty = Properties(created_at=created_at,lastupdated=lastupdated,status=status,unit=unit,subtype=subtype,city=city,locationtext=locationtext,building=building,bedrooms=bedrooms,price=price,description=description,assign_to=assign_to,owner_name=owner_name,owner_email=owner_email,owner_contact=owner_contact,plot=plot,bathrooms=bathrooms,street=street,source=source,furnished=furnished,title=title,commission=commission,deposit=deposit,created_by=created_by,completion_status=completion_status,parking=parking,owner=owner,type=type)
                    db.session.add(newproperty)
                    db.session.commit()
                    print("PROPERTY ADDED")
                    db.session.refresh(newproperty)
                    if (type == "Sale"):
                        newproperty.refno = 'UNI-S-'+str(newproperty.id)
                    else:
                        newproperty.refno = 'UNI-R-'+str(newproperty.id)
                    db.session.commit()                    
                line_count += 1
                print("Check marin jaani")
                print(line_count)
                if(line_count == 227):
                    break
        print(f'Processed {line_count} lines.')
    return jsonify(success=True)

#Property Finder API Integration

def propertyfinder01(): #generating token
    url = "https://api-v2.mycrm.com/token"
    payload = json.dumps({
        "grant_type": "password",
        "domain": "",
        "username": "",
        "password": "",
        "scope": "offline"
        })
    headers = {
        'Content-Type': 'application/json'
        }
    response = requests.request("POST", url, headers=headers, data=payload)
    x = json.loads(response.text)
    return (x["access_token"])


def locationid(community, location, access_token): #generating location ID
    if community == 'Contemporary Village':
        community = 'Contemporary Style'
    else:
        pass
    if community == 'Arabian Village':
        community = 'Arabian Style'
    else:
        pass
    if community == 'Desert Village':
        community = 'Desert Style'
    else:
        pass
    if location == 'Al Reef Villas':
        location = 'Al Reef'
    else:
        pass
    if community[:17] == 'Meera Shams Tower':
        community = 'Meera Shams'
    else:
        pass
    if community[:11] == 'Amaya Tower':
        community = 'Amaya Towers'
    else:
        pass
    community = community.replace(" ","_")
    community = community.replace("'","")
    location = location
    url = "https://api-v2.mycrm.com/locations?filters[string]="+community
    payload = ""
    headers = {
        'Authorization': 'Bearer '+access_token
        }
    response = requests.request("GET", url, headers=headers, data=payload)
    x = json.loads(response.text)
    y = x['location']
    w=''
    for a in range(len(y)):
        if y[a]['community'] == location:
            w = y[a]['id']
            break
        else:
            continue
    return (w)
    

#@handleproperties.route('/propertyfinder_advert/<pf_id>',methods = ['GET','POST']) # getting posted property ad link
#@login_required
def propertyfinder_advert(pf_id, access_token, refno):
    #access_token = propertyfinder01()
    url = "http://api-v2.mycrm.com/properties/"+str(pf_id)
    payload = ""
    headers = {
        'Authorization': 'Bearer '+access_token
        }
    response = requests.request("GET", url, headers=headers, data=payload)
    x = json.loads(response.text)
    y=x['property']['import']['propertyfinder']['id']
    y=y.split('-')
    print(y[-1])
    w = propertyfinder(refno=refno)
    if (w['type'] == "Sale"):
        tag = "buy"
    else:
        tag = "rent" 
    loctext=w['locationtext'].replace(" ","-").replace("'","").lower()
    build=w['building'].replace(" ","-").replace("'","").lower()
    website="https://www.propertyfinder.ae/en/plp/"+tag+"/"+w['subtype'].lower()+"-for-"+w['type'].lower()+"-abu-dhabi-"+loctext+"-"+build+"-"+y[-1]+".html"
    return(website)


@handleproperties.route('/propertyfinder03/<refno>',methods = ['GET','POST']) # creating properties 
@login_required
def propertyfinder03(refno):
    print("lets_start")
    url = "https://api-v2.mycrm.com/properties"
    access_token = propertyfinder01()
    w = propertyfinder(refno)
    loc = locationid(community = w["building"], location = w["locationtext"], access_token=access_token)
    print(loc)
    rentorsale = w["refno"][4:5]
    if (rentorsale == "R"):
        offering = 'rent'
        valueS = None
        period = 'year'
        default_period = 'year'
        valueR = w['price']
        cheques = 3
    else:
        offering = 'sale'
        valueS = w['price']
        period = None
        default_period = None
        valueR = None
        cheques = None
    priv = w['privateamenities'].split(",")
    prop = w['commercialamenities'].split(",")
    amen = priv+prop
    amenety=amenities(amen)
    typeid=type_id(w['subtype'])
    images = w['photos'].split("|")
    imagetoken=image_token(data=images, access_token=access_token)
    payload = json.dumps({
        "property": {
            "draft": False,
            "user": 77167,
            "bathrooms": w["bathrooms"], 
            "bedrooms": w["bedrooms"],
            "project_status": w['completion_status'],
            "size": w["size"],
            "built_up_area": w["size"],
            "type": typeid,
            "status": w["status"].lower(),
            "languages": {
            "en": {
                "title": w["title"],
                "description": w["description"]
            }
            },
            "location": {
                "id":loc
            },
            "price": {
                "offering_type":offering,
                "value": valueS,
                "default_period": default_period,
                "cheques": cheques,
                "prices": [
                    {
                    "period":period,
                    "value":valueR
                }
                ]
            },
            "views": {
                "view": w["view"]
            },
            "publication": {
                "genericportal": True,
                "privatesite": True,
                "propertyfinder": True,
            },
            "amenities": amenety,
            "images": imagetoken
            }
        })
    headers = {
        'Authorization': 'Bearer '+access_token
        }
    message=[]
    try:
        print(payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        x = json.loads(response.text)
        x1 = x['property']['id']
        db_update(refno=w['refno'],data=x1)
        message.append("Property posted successfully")
    except:
        message.append(str(x))
    try:
        website=propertyfinder_advert(pf_id=x1, access_token=access_token, refno=w['refno'])
        f = []
        f.append(str(x1))
        f.append(website)
        k = "|".join(f)
        db_update(refno=w['refno'],data=k)
        message.append("Website Link generated succesfully")
    except:
        message.append("WEBSITE GENERATION FAILED")
    message01 = "|".join(message)
    return jsonify(message01)


@handleproperties.route('/propertyfinder/<refno>',methods = ['GET','POST']) #getting property data from in-house CRM
@login_required
def propertyfinder(refno):
    lesssgooo = db.session.query(Properties).filter_by(refno = refno).first()
    all_property = []
    propertyObj = {}
    propertyObj = vars(lesssgooo)
    propertyObj.pop('_sa_instance_state')
    all_property.append(propertyObj) 
    return (propertyObj)


def image_token(data, access_token):
    imagetoken = []
    dub=1
    for i in data:
        print(i)
        data01=i.split("/")
        data02=data01[-1].split(".")
        url = "https://api-upload.mycrm.com/upload?type=property_image"
        payload={}
        files=[
            ('file',(data01[-1],open(i[1:],'rb'),'image/jpeg'))
            ]
        headers = {
            'Authorization': 'Bearer '+access_token
            }
        try:
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            x = json.loads(response.text)
            print(x)
            y = x['upload']['token']
            imagetoken.append({"image":{"token":y, "order":dub}})
            dub+=1
        except:
            print("Not Happening")   
    return(imagetoken)

def amenities(amen):
    f = open('PF_amenities.json')
    f1 = json.load(f)
    f2 = f1['amenities']
    amenity = []
    for i in amen:
        for j in f2:
            if i == j["name"]:
                amenity.append(j["id"])
            else:
                continue
    return(amenity)

def type_id(typeid):
    f = open('PF_amenities.json')
    f1 = json.load(f)
    f2 = f1['Type']
    for j in f2:
        if typeid == j["name"]:
            typeid1=j["id"]
            break
        else:
            continue
    return(typeid1)


def db_update(refno, data):
    all_leads = db.session.query(Properties).filter(Properties.refno == refno)
    for i in all_leads:
        i.property_finder = data
        db.session.commit()
    return ("ok")

def db_downdate(refno):
    all_leads = db.session.query(Properties).filter(Properties.refno == refno)
    for i in all_leads:
        i.property_finder = None
        db.session.commit()
    return ("ok")

@handleproperties.route('/delete_pf/<refno>',methods = ['GET','POST'])
@login_required
def delete_pf(refno):
    access_token = propertyfinder01()
    w = propertyfinder(refno)
    k=w['property_finder'].split('|')
    try:
        url = "https://api-v2.mycrm.com/properties/"+k[0]
        payload = ""
        headers = {
            'Authorization': 'Bearer '+access_token
            }
        response = requests.request("DELETE", url, headers=headers, data=payload)
        db_downdate(refno=w['refno'])
        print("Deleted Successfully")
        return jsonify(success=True)
    except:
        print("Could NOT be deleted")
        return jsonify(success=True)
    

@handleproperties.route('/testingnaaa',methods = ['GET','POST'])
@login_required
def testing():
    access_token = propertyfinder01()
    x = 3743443
    dub = propertyfinder_advert(pf_id=x, access_token=access_token, refno='UNI-S-4404')
    f = []
    f.append(str(x))
    f.append(dub)
    k = "|".join(f)
    db_update(refno='UNI-S-4404',data=k)
    return(dub)

@handleproperties.route('/testing_loc',methods = ['GET','POST'])
@login_required
def testing_loc():
    access_token = propertyfinder01()
    f = open('contacts.json')
    f1 = json.load(f)
    f2 = f1['ABD']
    h = open('sublocation.json')
    h1 = json.load(h)
    for i in f2[0]:
        if f2[0][i] == 'Al Reem Island':
            for j in h1[i[1:]]:
                if h1[i[1:]][j] == 'Amaya Tower 2':
                    print(h1[i[1:]][j])
                    x=locationid(community=h1[i[1:]][j], location=f2[0][i], access_token=access_token)
                    print(x)
                else:
                    pass
        else:
            pass
    return('ok')

@handleproperties.route('/find_that_link/<pfno>/<refno>',methods = ['GET','POST'])
@login_required
def find_that_link(pfno, refno):
    access_token = propertyfinder01()
    website=propertyfinder_advert(pf_id=pfno, access_token=access_token, refno=refno)
    f = []
    f.append(pfno)
    f.append(website)
    k = "|".join(f)
    db_update(refno=refno,data=k)
    return('ok')

@handleproperties.route('/delete_that_link/<refno>',methods = ['GET','POST'])
@login_required
def delete_that_link(refno):
    db_downdate(refno)
    return('ok')


@handleproperties.route('/propertyfinder07/<refno>',methods = ['GET','POST']) # updating properties 
@login_required
def propertyfinder07(refno):
    access_token = propertyfinder01()
    w = propertyfinder(refno)
    x = w['property_finder'].split('|')
    y = define_listing_level(pf_id=x[0], access_token=access_token)
    url = "https://api-v2.mycrm.com/properties/"+x[0]
    try:
        payload = json.dumps({
            "operations": [
                {
                    "op": "replace",
                    "path": "/listing_level",
                    "value": {
                        "listing_level": y,
                        "product_id": "ca731c8c-98fd-11ea-a2d4-ad21ef03ed0a",
                        "renewal": 0
                    }
                    }
                ]
                })
        headers = {
            'Authorization': 'Bearer '+access_token,
            'Content-Type': 'application/json'
            }
        response = requests.request("PATCH", url, headers=headers, data=payload)
        message = "Your property has been successfully updated on property finder"
    except:
        message = "Property update FAILED"
    return jsonify(message)

def define_listing_level(pf_id, access_token):
    url = "http://api-v2.mycrm.com/properties/"+str(pf_id)
    payload = ""
    headers = {
        'Authorization': 'Bearer '+access_token
        }
    response = requests.request("GET", url, headers=headers, data=payload)
    x = json.loads(response.text)
    y=x['property']['listing_level']
    return(y)

@handleproperties.route('/bulk_update/<arr>',methods = ['GET','POST']) # updating properties 
@login_required
def bulk_update(arr):
    access_token = propertyfinder01()
    arr_01 = arr.split(',')
    messages = []
    for i in arr_01:
        w = bulk_update_loop(refno=i,access_token=access_token)
        messages.append(w)
    return jsonify(messages)

def bulk_update_loop(refno, access_token):
    w = propertyfinder(refno)
    x = w['property_finder'].split('|')
    y = define_listing_level(pf_id=x[0], access_token=access_token)
    url = "https://api-v2.mycrm.com/properties/"+x[0]
    try:
        payload = json.dumps({
            "operations": [
                {
                    "op": "replace",
                    "path": "/listing_level",
                    "value": {
                        "listing_level": y,
                        "product_id": "ca731c8c-98fd-11ea-a2d4-ad21ef03ed0a",
                        "renewal": 0
                    }
                    }
                ]
                })
        headers = {
                'Authorization': 'Bearer '+access_token,
                'Content-Type': 'application/json'
                }
        response = requests.request("PATCH", url, headers=headers, data=payload)
        message = refno+" has been successfully updated on property finder"
    except:
        message = refno+" update FAILED"
    return(message)


#def image_id(data, access_token, loc):
#    access_token = propertyfinder01()
#    url = "http://api-v2.mycrm.com/properties?filters[status]=available"
#    payload = ""
#    headers = {
#        'Authorization': 'Bearer '+access_token
#        }
#    response = requests.request("GET", url, headers=headers, data=payload)
#    x = json.loads(response.text)
#    return(x)

@handleproperties.route('/bigboytesting',methods = ['GET','POST']) #to checkd duplicate properties
@login_required
def bigboytesting():
    print("lets start")
    lesssgooo = db.session.query(Properties)
    a=[]
    for i in lesssgooo:
        a.append({'location':i.locationtext, 'Community':i.building, 'Unit':i.unit, 'Refno': i.refno})
    b = a
    x=0
    for i in range(len(a)):
        dub = 0
        w=[]
        for j in range(len(b)):
            if a[i]['location'] == b[j]['location'] and a[i]['Community'] == b[j]['Community'] and a[i]['Unit'] == b[j]['Unit'] and b[j]['location'] != 'locationtext':
                dub+=1
                if dub > 1:
                    w.append({b[j]['Refno']})
                    b[j]={'location':'locationtext', 'Community':'building', 'Unit':'unit'}
                    x+=1
        if dub > 1:
            w.append({a[i]['Refno']})
            print(w)
    print(x)
    return ('ok')