from forms import AddEmployeeForm, AddUserForm
from operator import methodcaller
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import Employees, User
import json
import os 
from werkzeug.security import generate_password_hash
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

handleemployees = Blueprint('handleemployees', __name__, template_folder='templates')



@handleemployees.route('/human_resource/employees',methods = ['GET','POST'])
@login_required
def display_employees():   
    if current_user.sale == False:
        return abort(404)
    data = []
    existing_users = []
    for a in db.session.query(User).all():
        existing_users.append(a.username)
    if current_user.viewall == True:
        for r in db.session.query(Employees).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            #for k in ['photos','commercialtype','title','description','unit','plot','street','sizeunits','price','rentpriceterm','pricecurrency','totalclosingfee','annualcommunityfee','lastupdated','contactemail','contactnumber','locationtext','furnished','propertyamenities','commercialamenities','geopoint','bathrooms','price_on_application','rentispaid','permit_number','view360','video_url','completion_status','source','owner']: new.pop(k)
            if current_user.edit == True:
                edit_btn =  '<a href="/edit_employee/'+str(new['id'])+'"><button  class="btn btn-primary si">Edit</button></a><a href="/delete_employee/'+str(new['id'])+'"><button class="btn btn-danger si">Delete</button></a>'
            else:
                edit_btn = ''
            
            if r.Name in existing_users:
                account = ""
            else:
                account = '<a href="/add_employee_account/'+str(new['id'])+'"><button  class="btn btn-info si">Sign Up</button></a>'

            new["edit"] = "<div style='display:flex;'>"+edit_btn+account+"</div>"
            data.append(new)
    else:
        for r in db.session.query(Employees).filter(Employees.created_by == current_user.username):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            #for k in ['photos','commercialtype','title','description','unit','plot','street','sizeunits','price','rentpriceterm','pricecurrency','totalclosingfee','annualcommunityfee','lastupdated','contactemail','contactnumber','locationtext','furnished','propertyamenities','commercialamenities','geopoint','bathrooms','price_on_application','rentispaid','permit_number','view360','video_url','completion_status','source','owner']: new.pop(k)
            if current_user.edit == True:
                edit_btn =  '<a href="/edit_employee/'+str(new['id'])+'"><button  class="btn btn-primary si">Edit</button></a><a  href="/delete_employee/'+str(new['id'])+'"><button class="btn btn-danger si">Delete</button></a>'
            else:
                edit_btn = ''
            if r.Name in existing_users:
                account = ""
            else:
                account = '<a href="/add_employee_account/'+str(new['id'])+'"><button  class="btn btn-info si">Sign Up</button></a>'

            new["edit"] = "<div style='display:flex;'>"+edit_btn+account+"</div>"
            data.append(new)

    f = open('employee_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('employees.html', data = data , columns = columns)



@handleemployees.route('/add_employee/', methods = ['GET','POST'])
@login_required
def add_employee():
    if current_user.hr == False:
        return abort(404)  
    form = AddEmployeeForm()
    if request.method == 'POST':
        Status = form.Status.data
        Employee_Status = form.Employee_Status.data
        Employee_ID = form.Employee_ID.data
        Name = form.Name.data
        Position = form.Position.data
        Nationality = form.Nationality.data
        UID = form.UID.data
        Date_of_Birth = form.Date_of_Birth.data
        Date_of_Joining = form.Date_of_Joining.data
        Emirates_ID = form.Emirates_ID.data
        Card_No = form.Card_No.data
        Emirates_Card_Expiry = form.Emirates_Card_Expiry.data
        Mobile_No = form.Mobile_No.data
        MOL_Personal_No = form.MOL_Personal_No.data
        Labor_Card_No = form.Labor_Card_No.data
        Labor_Card_Expiry = form.Labor_Card_Expiry.data
        Insurance_No = form.Insurance_No.data
        Insurance_Effective_Date = form.Insurance_Effective_Date.data
        Insurance_Expiry_Date = form.Insurance_Expiry_Date.data
        Date_of_Submission = form.Date_of_Submission.data
        Residence_Expiry = form.Residence_Expiry.data
        Remarks = form.Remarks.data
        created_by = current_user.username
        employee = Employees(created_by = created_by, Status = Status,  Employee_Status = Employee_Status,  Employee_ID = Employee_ID,  Name = Name,  Position = Position,  Nationality = Nationality,  UID = UID,  Date_of_Birth = Date_of_Birth,  Date_of_Joining = Date_of_Joining,  Emirates_ID = Emirates_ID,  Card_No = Card_No,  Emirates_Card_Expiry = Emirates_Card_Expiry,  Mobile_No = Mobile_No,  MOL_Personal_No = MOL_Personal_No,  Labor_Card_No = Labor_Card_No,  Labor_Card_Expiry = Labor_Card_Expiry,  Insurance_No = Insurance_No,  Insurance_Effective_Date = Insurance_Effective_Date,  Insurance_Expiry_Date = Insurance_Expiry_Date,  Date_of_Submission = Date_of_Submission,  Residence_Expiry = Residence_Expiry,  Remarks = Remarks)
        db.session.add(employee)
        db.session.commit()
        return redirect(url_for('handleemployees.display_employees'))
    return render_template('add_employee.html', form=form, user = current_user.username)


@handleemployees.route('/edit_employee/<var>', methods = ['GET','POST'])
@login_required
def edit_employee(var):
    if current_user.hr == False or current_user.edit == False:
        return abort(404) 
    edit = db.session.query(Employees).filter_by(id = var).first()
    form = AddEmployeeForm(obj = edit)
    if request.method == 'POST':
        form.populate_obj(edit)
        db.session.commit()
        return redirect(url_for('handleemployees.display_employees'))
    return render_template('add_employee.html',form=form)


@handleemployees.route('/add_employee_account/<var>', methods = ['GET','POST'])
@login_required
def add_employee_account(var):
    if current_user.hr == False:
        return abort(404) 
    edit = db.session.query(Employees).filter_by(id = var).first()
    account = User(username=edit.Name.replace(" ","_") ,password="", number=edit.Mobile_No, email = "", job_title = edit.Position)
    form = AddUserForm(obj = account)
    if request.method == 'POST':
        form.populate_obj(edit)
        passer = generate_password_hash(form.password.data,method='sha256')
        newuser = User(username=form.username.data, password=passer, number=form.number.data, email = form.email.data, job_title = form.job_title.data, department = form.department.data)
        db.session.add(newuser)
        db.session.commit()
        return redirect(url_for('handleemployees.display_employees'))
    return render_template('create_user_hr.html',form=form)


@handleemployees.route('/delete_employee/<var>', methods = ['GET','POST'])
@login_required
def delete_employee(var):
    if current_user.hr == False or current_user.edit == False:
        return abort(404) 
    emp = db.session.query(Employees).filter_by(id = var).first()
    db.session.delete(emp)
    db.session.commit()
    return redirect(url_for('handleemployees.display_employees'))
    