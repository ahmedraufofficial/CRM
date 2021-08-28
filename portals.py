from models import Properties
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint, jsonify, make_response, render_template
import xml.etree.cElementTree as e
from datetime import datetime

db = SQLAlchemy()

portals = Blueprint('portals', __name__, template_folder='templates')

@portals.route('/bayut',methods = ['GET','POST'])
def bayut():
    data = []
    for r in db.session.query(Properties).all():
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        data.append(new)

    r = e.Element("Listings")
    for i in data:
        z = 1
        if i['type'] == "Rent":
            listing = e.SubElement(r,"Listing")
            e.SubElement(listing,"Count").text = str(z)
            e.SubElement(listing,"Unit_Type").text = i['subtype']
            e.SubElement(listing,"Ad_Type").text = i['type']
            e.SubElement(listing,"Emirate").text = i['city']
            e.SubElement(listing,"Community").text = i['locationtext']
            e.SubElement(listing,"Property_Name").text = i['building']
            e.SubElement(listing,"Property_Ref_No").text = i['refno']
            e.SubElement(listing,"Price").text = i['price']
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
            Facilities = e.SubElement(listing,"Facilities")
            e.SubElement(listing,"unit_measure").text = "Sq.Ft."
            if i['building'] == 'Sky Tower':
                lat = 24.493895
                lon = 54.410740
            elif i['building'] == 'Sun Tower':
                lat = 24.496193
                lon = 54.406832
            elif i['building'] == 'The Gate Tower 1':
                lat = 24.494051
                lon = 54.407362
            Geopoints = e.SubElement(listing,"Geopoints")
            e.SubElement(Geopoints,"Latitude").text = str(lat)
            e.SubElement(Geopoints,"Longitude").text = str(lon)
            e.SubElement(listing,"featured_on_companywebsite").text = "false"
            e.SubElement(listing,"under_construction").text = "false"
            e.SubElement(listing,"Off_Plan").text = "No"
            Views = e.SubElement(listing,"Views")
            e.SubElement(listing,"Cheques").text = "0"
            e.SubElement(listing,"Exclusive_Rights").text = "No"

        else:
            listing = e.SubElement(r,"Listing")
            e.SubElement(listing,"Count").text = str(z)
            e.SubElement(listing,"Unit_Type").text = str(z)
            e.SubElement(listing,"Ad_Type").text = str(z)
            e.SubElement(listing,"Emirate").text = str(z)
            e.SubElement(listing,"Community").text = str(z)
            e.SubElement(listing,"Property_Name").text = str(z)
            e.SubElement(listing,"Property_Ref_No").text = str(z)
            e.SubElement(listing,"Price").text = str(z)
            e.SubElement(listing,"Unit_Builtup_Area").text = str(z)
            e.SubElement(listing,"No_of_Rooms").text = str(z)
            e.SubElement(listing,"No_of_Bathrooms").text = str(z)
            e.SubElement(listing,"Property_Title").text = str(z)
            e.SubElement(listing,"Web_Remarks").text = str(z)
            e.SubElement(listing,"Listing_Agent").text = str(z)
            e.SubElement(listing,"Listing_Agent_Phone").text = str(z)
            e.SubElement(listing,"Listing_Agent_Email").text = str(z)
            #e.SubElement(listing,"Images").text = str(z)
            e.SubElement(listing,"Listing_Date").text = str(z)
            e.SubElement(listing,"Last_Updated").text = str(z)
            #e.SubElement(listing,"Facilities").text = str(z)
            e.SubElement(listing,"unit_measure").text = str(z)
            #e.SubElement(listing,"Geopoints").text = str(z)
            e.SubElement(listing,"featured_on_companywebsite").text = str(z)
            e.SubElement(listing,"under_construction").text = str(z)
            e.SubElement(listing,"Off_Plan").text = str(z)
            e.SubElement(listing,"Views").text = str(z)
            e.SubElement(listing,"Cheques").text = str(z)
            e.SubElement(listing,"Exclusive_Rights").text = str(z)
        
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
    