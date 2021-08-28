from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import Properties
from forms import AddPropertyForm
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
import glob
from functions import logs, notes, add_user_list
from sqlalchemy import or_

a = os.getcwd()
UPLOAD_FOLDER = os.path.join(a+'/static', 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)




db = SQLAlchemy()

handleproperties = Blueprint('handleproperties', __name__, template_folder='templates')

@handleproperties.route('/properties',methods = ['GET','POST'])
@login_required
def display_properties():
    if current_user.listing == False:
        return abort(404)
    data = []
    if current_user.viewall == True:
        for r in db.session.query(Properties).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['photos','title','description','unit','plot','street','rentpriceterm','lastupdated','contactemail','contactnumber','furnished','privateamenities','commercialamenities','geopoint','bathrooms','permit_number','view360','video_url','completion_status','source','owner','tenant','parking','featured','offplan_status','tenure','expiry_date','deposit','commission','price_per_area','plot_size']: new.pop(k)
            if current_user.edit == True:
                edit_btn = '<a class="btn btn-primary si" href="/edit_property/'+str(new['refno'])+'"><i class="bi bi-pencil"></i></a>'
            else:
                edit_btn = ''
            new["edit"] ="<div style='display:flex;'>"+ edit_btn +'<button class="btn btn-danger si"  onclick="view_property('+"'"+new['refno']+"'"+')"><i class="bi bi-aspect-ratio"></i></button>'+'<button class="btn btn-warning si" style="color:white;" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-plus"></i></button>'+"</div>"
            data.append(new)
    else:
        for r in db.session.query(Properties).filter(or_(Properties.created_by == current_user.username,Properties.assign_to == current_user.username)):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['photos','title','description','unit','plot','street','rentpriceterm','lastupdated','contactemail','contactnumber','furnished','privateamenities','commercialamenities','geopoint','bathrooms','permit_number','view360','video_url','completion_status','source','owner','tenant','parking','featured','offplan_status','tenure','expiry_date','deposit','commission','price_per_area','plot_size']: new.pop(k)
            if current_user.edit == True:
                edit_btn = '<a class="btn btn-primary si" href="/edit_property/'+str(new['refno'])+'"><i class="bi bi-pencil"></i></a>'
            else:
                edit_btn = ''
            new["edit"] ="<div style='display:flex;'>"+ edit_btn +'<button class="btn btn-danger si"  onclick="view_property('+"'"+new['refno']+"'"+')"><i class="bi bi-aspect-ratio"></i></button>'+'<button class="btn btn-warning si" style="color:white;" onclick="view_note('+"'"+new['refno']+"'"+')"><i class="bi bi-journal-plus"></i></button>'+"</div>"
            data.append(new)
    f = open('property_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('properties.html', data = data , columns = columns, user = current_user.username)

    
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
        #lastupdated = form.lastupdated.data
        w = open('abudhabi.json')
        file_data = json.load(w)
        locationtext = file_data[form.locationtext.data]
        furnished = form.furnished.data
        parking = form.parking.data
        featured = form.featured.data
        building = form.building.data
        privateamenities = ",".join(form.privateamenities.data)
        commercialamenities = ",".join(form.commercialamenities.data)
        #geopoint = form.geopoint.data
        bathrooms = form.bathrooms.data
        permit_number = form.permit_number.data
        view360 = form.view360.data
        video_url = form.video_url.data 
        commission = form.commission.data
        deposit = form.deposit.data 
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
        newproperty = Properties(commission = commission,deposit=deposit,owner_name=owner_name,owner_contact=owner_contact,owner_email=owner_email,contactemail=contactemail,contactnumber=contactnumber,featured=featured,parking=parking,tenant=tenant,expiry_date=expiry_date,price_per_area = price_per_area,plot_size = plot_size,status = status,city = city,type = type,subtype = subtype,title = title,description = description,size = size,price = price,rentpriceterm = rentpriceterm,bedrooms = bedrooms,locationtext = locationtext,furnished = furnished,building = building,privateamenities = privateamenities,bathrooms = bathrooms,permit_number = permit_number,view360 =  view360,video_url = video_url,source=source,owner=owner,assign_to=assign_to,unit=unit,plot=plot,street=street,commercialamenities=commercialamenities,created_by=current_user.username)
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
        #lastupdated = form.lastupdated.data
        w = open('abudhabi.json')
        file_data = json.load(w)
        locationtext = file_data[form.locationtext.data]
        furnished = form.furnished.data
        parking = form.parking.data
        featured = form.featured.data
        building = form.building.data
        privateamenities = ",".join(form.privateamenities.data)
        commercialamenities = ",".join(form.commercialamenities.data)
        #geopoint = form.geopoint.data
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
        commission = form.commission.data
        deposit = form.deposit.data 
        assigned = form.assign_to.data
        assigned = assigned.split('|')
        assign_to = assigned[0]
        contactemail = assigned[2]
        contactnumber = assigned[1]
        newproperty = Properties(commission = commission,deposit=deposit,owner_name=owner_name,owner_contact=owner_contact,owner_email=owner_email,contactemail=contactemail,contactnumber=contactnumber,offplan_status = offplan_status, completion_date = completion_date,tenure=tenure,featured=featured,parking=parking,expiry_date=expiry_date,price_per_area = price_per_area,plot_size = plot_size,status = status,city = city,type = type,subtype = subtype,title = title,description = description,size = size,price = price,bedrooms = bedrooms,locationtext = locationtext,furnished = furnished,building = building,privateamenities = privateamenities,bathrooms = bathrooms,permit_number = permit_number,view360 =  view360, video_url = video_url, completion_status = completion_status,source=source,owner=owner,assign_to=assign_to,unit=unit,plot=plot,street=street,commercialamenities=commercialamenities,created_by=current_user.username)
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
    if edit.privateamenities != None:
        edit.privateamenities = edit.privateamenities.split(',')
    if edit.commercialamenities != None:
        edit.commercialamenities = edit.commercialamenities.split(',')
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
    return render_template('add_property.html', form=form, radio_enable = 'enabled',community=edit.locationtext, building = edit.building, purpose=category, assign=edit.assign_to,user=current_user.username)


@handleproperties.route('/community/<location>',methods = ['GET','POST'])
@login_required
def community(location):
    a = location
    f = open('sublocation.json')
    file_data = json.load(f)
    try:
        locs = file_data[a[1:]]
    except:
        locs = file_data[a]
    locs = list(locs.values())
    locations = []
    for i in locs:
        locations.append((i,i))
    return jsonify({'locations':locations})