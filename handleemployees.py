from forms import AddEmployeeForm, AddUserForm, AddExitformentry, AddLeaveformentry
from operator import methodcaller
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import Employees, User, Exitform, Leaveform
import json
import os 
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import datetime, timedelta,time
from functions import *
from sqlalchemy import or_
import glob

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path+'/static', 'uploads02')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)




db = SQLAlchemy()

handleemployees = Blueprint('handleemployees', __name__, template_folder='templates')



@handleemployees.route('/human_resource/employees',methods = ['GET','POST'])
@login_required
def display_employees():  
    sesh = db.session.query(Employees).filter_by(crm_username="ahmed")
    for i in sesh:
        x = i.Remarks
        y = i.Employee_ID
        z = i.documents
    form = AddEmployeeForm() 

    if request.method == 'POST':
        files_filenames = []
        try:
            for filex in form.documents.data:
                file_filename = secure_filename(filex.filename)
                directory = UPLOAD_FOLDER+'/E-'+str(y)
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                filex.save(os.path.join(directory, file_filename))
                files_filenames.append('/static/uploads02'+'/E-'+str(y)+"/"+file_filename)
            sesh = db.session.query(Employees).filter_by(crm_username="ahmed")
            for i in sesh:
                i.documents =  '|'.join(files_filenames)
            db.session.commit()
            print("Lesssgooo")
        except:
            print("Nahhhh")
        return redirect(url_for('handleemployees.display_employees'))

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
            if current_user.edit == True:
                edit_btn =  '<a href="/edit_employee/'+str(new['id'])+'"><button  class="btn btn-primary si">Edit</button></a><a href="/delete_employee/'+str(new['id'])+'"><button class="btn btn-danger si">Delete</button></a>'+'<button class="btn btn-warning si" style="color:white;" data-toggle="modal" data-target="#detailsModal" onclick="view_details('+"'UNI-E-"+new['Employee_ID']+"'"+')">Details</button>'
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
    return render_template('employees.html', data = data , columns = columns, user=current_user, line_manager = x, form=form, documents = z)



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
        crm_usrname = form.crm_username.data
        documents = form.documents.data
        created_by = current_user.username
        employee = Employees(created_by = created_by, Status = Status,  Employee_Status = Employee_Status,  Employee_ID = Employee_ID,  Name = Name,  Position = Position,  Nationality = Nationality,  UID = UID,  Date_of_Birth = Date_of_Birth,  Date_of_Joining = Date_of_Joining,  Emirates_ID = Emirates_ID,  Card_No = Card_No,  Emirates_Card_Expiry = Emirates_Card_Expiry,  Mobile_No = Mobile_No,  MOL_Personal_No = MOL_Personal_No,  Labor_Card_No = Labor_Card_No,  Labor_Card_Expiry = Labor_Card_Expiry,  Insurance_No = Insurance_No,  Insurance_Effective_Date = Insurance_Effective_Date,  Insurance_Expiry_Date = Insurance_Expiry_Date,  Date_of_Submission = Date_of_Submission,  Residence_Expiry = Residence_Expiry,  Remarks = Remarks, crm_usrname = crm_usrname, documents = documents)
        db.session.add(employee)
        db.session.commit()
        additional_details('UNI-E-' + str(Employee_ID))
        print("here")
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
    return render_template('add_employee.html',form=form, radio_enable = 'enabled')


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
        create_json(form.username.data)
        logs(form.username.data,form.username.data,"Created")
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

#EXIT FORMS

@handleemployees.route('/human_resource/exit_forms',methods = ['GET','POST'])
@login_required
def display_exitforms():
    if current_user.listing == False and current_user.sale == False:
        return abort(404)
    data = []
    if current_user.is_admin == True or current_user.job_title == "HR Manager":
        for r in db.session.query(Exitform).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason', 'extra01']: new.pop(k)
            edit_btn = '<a href="/edit_exitform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
            delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            new["edit"] = "<div style='display:flex;'>"+edit_btn+delete_btn+"</div>"
            new['date_from'] = new['date_from'][:10]
            new['date_to'] = new['date_to'][:10]
            data.append(new)
    elif current_user.job_title == "Manager":
        for r in db.session.query(Exitform).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason', 'extra01']: new.pop(k)
            if new['hr_approval'] == "Pending":
                edit_btn = '<a href="/edit_exitform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
                delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            else:
                edit_btn = "Request Closed"
                delete_btn = ''
            new["edit"] = "<div style='display:flex;'>"+edit_btn+delete_btn+"</div>"
            new['date_from'] = new['date_from'][:10]
            new['date_to'] = new['date_to'][:10]
            data.append(new)
    elif current_user.sale == True or current_user.listing == True or current_user.department == "Marketing":
        for r in db.session.query(Exitform).filter(Exitform.created_by == current_user.username):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason', 'extra01']: new.pop(k)
            if new['manager_approval'] == "Pending":
                edit_btn = '<a href="/edit_exitform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
            else:
                edit_btn = "Request Closed"
            new["edit"] = "<div style='display:flex;'>"+edit_btn+"</div>"
            new['date_from'] = new['date_from'][:10]
            new['date_to'] = new['date_to'][:10]
            data.append(new)
    f = open('exitform_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).all()
    return render_template('exit_forms.html', data = data , columns = columns, user = current_user.username, all_users = all_users)

@handleemployees.route('/add_exitform', methods = ['GET','POST'])
@login_required
def add_exit_form(): 
    form = AddExitformentry()
    if request.method == 'POST': 
        name = form.name.data
        designation = form.designation.data
        department = form.department.data
        date_from = form.date_from.data
        date_to = form.date_to.data
        time_from = form.time_from.data
        time_to = form.time_to.data
        reason = form.reason.data
        viewing_lead = form.viewing_lead.data
        if form.manager_approval.data != None:
            manager_approval = form.manager_approval.data
        else:
            manager_approval = 'Pending'
        hr_acknowledge = form.hr_acknowledge.data
        if form.hr_approval.data != None:
            hr_approval = form.hr_approval.data
        else:
            hr_approval = 'Pending'
        remarks = form.remarks.data
        created_date = datetime.now()+timedelta(hours=4)
        updated_date = datetime.now()+timedelta(hours=4)
        created_by = current_user.username
        newexitform = Exitform(name=name, designation=designation, department=department, reason=reason, viewing_lead=viewing_lead, remarks=remarks, date_from=date_from, date_to=date_to, time_from=time_from, time_to=time_to, hr_acknowledge=hr_acknowledge, created_date = created_date, updated_date = updated_date, created_by = created_by, manager_approval = manager_approval, hr_approval = hr_approval)

        db.session.add(newexitform)
        db.session.commit()
        db.session.refresh(newexitform)
        newexitform.refno = 'E-F-'+str(newexitform.id)
        db.session.commit()

        return redirect(url_for('handleemployees.display_exitforms'))
    return render_template('add_exitform.html', form=form, user = current_user.username)

@handleemployees.route('/edit_exitform/<variable>', methods = ['GET','POST'])
@login_required
def edit_exitform(variable):
    edit = db.session.query(Exitform).filter_by(refno=variable).first()
    form = AddExitformentry(obj = edit)
    if request.method == 'POST':
        form.populate_obj(edit)
        edit.updated_date = datetime.now()+timedelta(hours=4)
        db.session.commit()
        return redirect(url_for('handleemployees.display_exitforms'))
    return render_template('add_exitform.html', form=form, user = current_user.username)

@handleemployees.route('/delete_exitform/<variable>', methods = ['GET','POST'])
@login_required
def delete_exitform(variable):
    delete = db.session.query(Exitform).filter_by(refno=variable).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('handleemployees.display_exitforms'))


#LEAVE FORMS

@handleemployees.route('/human_resource/leave_forms',methods = ['GET','POST'])
@login_required
def display_leaveforms():
    if current_user.listing == False and current_user.sale == False:
        return abort(404)
    data = []
    if current_user.is_admin == True or current_user.job_title == "HR Manager":
        for r in db.session.query(Leaveform).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason', 'updated_date', 'designation']: new.pop(k)
            edit_btn = '<a href="/edit_leaveform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
            delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            new["edit"] = "<div style='display:flex;'>"+edit_btn+delete_btn+"</div>"
            new['date_from'] = new['date_from'][:10]
            new['date_to'] = new['date_to'][:10]
            data.append(new)
    elif current_user.job_title == "Manager":
        for r in db.session.query(Leaveform).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason']: new.pop(k)
            if new['hr_approval'] == "Pending":
                edit_btn = '<a href="/edit_leaveform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
                delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            else:
                edit_btn = "Request Closed"
                delete_btn = ''
            new["edit"] = "<div style='display:flex;'>"+edit_btn+delete_btn+"</div>"
            new['date_from'] = new['date_from'][:10]
            new['date_to'] = new['date_to'][:10]
            data.append(new)
    elif current_user.sale == True or current_user.listing == True or current_user.department == "Marketing":
        for r in db.session.query(Leaveform).filter(Leaveform.created_by == current_user.username):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason']: new.pop(k)
            if new['manager_approval'] == "Pending":
                edit_btn = '<a href="/edit_leaveform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
            else:
                edit_btn = "Request Closed"
            new["edit"] = "<div style='display:flex;'>"+edit_btn+"</div>"
            new['date_from'] = new['date_from'][:10]
            new['date_to'] = new['date_to'][:10]
            data.append(new)
    f = open('leaveform_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).all()
    return render_template('leave_forms.html', data = data , columns = columns, user = current_user.username, all_users = all_users)

@handleemployees.route('/add_leaveform', methods = ['GET','POST'])
@login_required
def add_leave_form(): 
    form = AddLeaveformentry()
    if request.method == 'POST': 
        name = form.name.data
        designation = form.designation.data
        department = form.department.data
        employee_no = form.employee_no.data
        joining_date = form.joining_date.data
        leave_type = form.leave_type.data
        reason = form.reason.data
        date_from = form.date_from.data
        date_to = form.date_to.data
        no_of_days = form.no_of_days.data
        leave_balance = form.leave_balance.data

        manager_ack_date = form.manager_ack_date.data
        if form.manager_approval.data != None:
            manager_approval = form.manager_approval.data
        else:
            manager_approval = 'Pending'
        hr_ack_date = form.hr_ack_date.data
        if form.hr_approval.data != None:
            hr_approval = form.hr_approval.data
        else:
            hr_approval = 'Pending'
        remarks = form.remarks.data
        created_date = datetime.now()+timedelta(hours=4)
        updated_date = datetime.now()+timedelta(hours=4)
        created_by = current_user.username
        newleaveform = Leaveform(name=name, designation=designation, department=department, reason=reason, remarks=remarks, date_from=date_from, date_to=date_to, hr_ack_date=hr_ack_date, manager_ack_date=manager_ack_date, created_date = created_date, updated_date = updated_date, created_by = created_by, manager_approval = manager_approval, hr_approval = hr_approval, employee_no=employee_no, joining_date=joining_date, leave_type=leave_type, no_of_days=no_of_days, leave_balance=leave_balance)

        db.session.add(newleaveform)
        db.session.commit()
        db.session.refresh(newleaveform)
        newleaveform.refno = 'L-F-'+str(newleaveform.id)
        db.session.commit()

        return redirect(url_for('handleemployees.display_leaveforms'))
    return render_template('add_leaveform.html', form=form, user = current_user.username)

@handleemployees.route('/edit_leaveform/<variable>', methods = ['GET','POST'])
@login_required
def edit_leaveform(variable):
    edit = db.session.query(Leaveform).filter_by(refno=variable).first()
    form = AddLeaveformentry(obj = edit)
    if request.method == 'POST':
        form.populate_obj(edit)
        edit.updated_date = datetime.now()+timedelta(hours=4)
        db.session.commit()
        return redirect(url_for('handleemployees.display_leaveforms'))
    return render_template('add_leaveform.html', form=form, user = current_user.username)

@handleemployees.route('/delete_leaveform/<variable>', methods = ['GET','POST'])
@login_required
def delete_leaveform(variable):
    delete = db.session.query(Leaveform).filter_by(refno=variable).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('handleemployees.display_leaveforms'))
    
    