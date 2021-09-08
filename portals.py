from sqlalchemy.sql.elements import ColumnClause
from models import Properties
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, jsonify, make_response, render_template
import xml.etree.cElementTree as e
from datetime import datetime
import os
import json

db = SQLAlchemy()

portals = Blueprint('portals', __name__, template_folder='templates')

@portals.route('/bayut',methods = ['GET','POST'])
def bayut():
    data = []
    for r in db.session.query(Properties).all():
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        data.append(new)

    mapdir = os.getcwd() + '/'   
    f = open(os.path.join(mapdir+'bayut_mapping.json'))
    c = json.load(f)

    r = e.Element("Listings")
    for i in data:
        z = 1
        listing = e.SubElement(r,"Listing")
        e.SubElement(listing,"Count").text = str(z)
        e.SubElement(listing,"Unit_Type").text = i['subtype']
        e.SubElement(listing,"Ad_Type").text = i['type']
        e.SubElement(listing,"Emirate").text = i['city']
        e.SubElement(listing,"Community").text = i['locationtext']
        e.SubElement(listing,"Property_Name").text = i['building']
        e.SubElement(listing,"Property_Ref_No").text = i['refno']
        e.SubElement(listing,"Price").text = i['price']
        if i['type'] == "Rent":
            e.SubElement(listing,"Frequency").text = i['rentpriceterm']
        e.SubElement(listing,"Unit_Builtup_Area").text = i['size']
        e.SubElement(listing,"No_of_Rooms").text = i['bedrooms']
        e.SubElement(listing,"No_of_Bathrooms").text = i['bathrooms']
        e.SubElement(listing,"Property_Title").text = i['title']
        e.SubElement(listing,"Web_Remarks").text = i['description']
        e.SubElement(listing,"Listing_Agent").text = i['assign_to']
        e.SubElement(listing,"Listing_Agent_Phone").text = '+971-54-9981998'
        e.SubElement(listing,"Listing_Agent_Email").text = 'bayut3@uhpae.com'
        Images = e.SubElement(listing,"Images")
        a = i['photos'].split('|')
        for y in a:
            e.SubElement(Images,"ImageUrl").text = y
        e.SubElement(listing,"Listing_Date").text = str(datetime.now())
        e.SubElement(listing,"Last_Updated").text = str(datetime.now())
        Views = e.SubElement(listing,"Views")
        Facilities = e.SubElement(listing,"Facilities")
        f = i['privateamenities'].split(',') + i['commercialamenities'].split(',')
        for y in f:
            try:
                e.SubElement(Facilities,"Facility").text = c[y]
                if y == "View of Water":
                    e.SubElement(Views,"View").text = "Sea View"
                if y == "View of Landmark":
                    e.SubElement(Views,"View").text = "Community View"
            except:
                continue
        e.SubElement(listing,"unit_measure").text = "Sq.Ft."
        Geopoints = e.SubElement(listing,"Geopoints")
        try:
            e.SubElement(Geopoints,"Latitude").text = i['geopoint'].split(',')[0]
            e.SubElement(Geopoints,"Longitude").text = i['geopoint'].split(',')[1]
        except:
            e.SubElement(Geopoints,"Latitude").text = ""
            e.SubElement(Geopoints,"Longitude").text = ""

        e.SubElement(listing,"featured_on_companywebsite").text = "false"
        e.SubElement(listing,"under_construction").text = "false"
        e.SubElement(listing,"Off_Plan").text = "No"
        
        e.SubElement(listing,"Cheques").text = "0"
        e.SubElement(listing,"Exclusive_Rights").text = "No"
        z = z + 1

    a = e.ElementTree(r)
    print()
    a.write("template/bayut.xml")
    return jsonify(data[0])

@portals.route('/bayut/xml',methods = ['GET','POST'])
def bayut_xml():
    response= make_response(render_template('bayut.xml'))
    response.headers['Content-Type'] = 'application/xml'
    return response
    

@portals.route('/dubizzle',methods = ['GET','POST'])
def dubizzle():
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
        e.SubElement(listing,"status").text = "vacant"
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
        e.SubElement(listing,"geopoint").text = i['geopoint']
        e.SubElement(listing,"furnished").text = i['furnished']
        e.SubElement(listing,"permit_number").text = i['permit_number']
        e.SubElement(listing,"view360").text = i['view360']
        e.SubElement(listing,"video_url").text = i['video_url']
        e.SubElement(listing,"lastupdated").text = str(datetime.now())
        z = z + 1

    a = e.ElementTree(r)
    
    a.write("template/dubizzle.xml")
    return jsonify(data[0])

@portals.route('/dubizzle/xml',methods = ['GET','POST'])
def dubizzle_xml():
    response= make_response(render_template('dubizzle.xml'))
    response.headers['Content-Type'] = 'application/xml'
    return response