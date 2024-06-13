from forms import AddEmployeeForm, AddUserForm, AddExitformentry, AddLeaveformentry, Addadvanceform
from operator import methodcaller
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import Employees, User, Exitform, Leaveform, Advanceform
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
    if current_user.hr == False:
        return abort(404)
    data = []
    existing_users = []
    #for a in db.session.query(User).all():
    #    existing_users.append(a.username)
    if current_user.viewall == True:
        for r in db.session.query(Employees).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            if current_user.edit == True:
                edit_btn =  '<a href="/edit_employee/'+str(new['id'])+'"><button  class="btn btn-primary si"><i class="bi bi-pen"></i></button></a><a href="/delete_employee/'+str(new['id'])+'"><button class="btn btn-danger si"><i class="bi bi-trash"></i></button></a>'+'<button class="btn btn-warning si" style="color:white;" data-toggle="modal" data-target="#detailsModal" onclick="view_details('+"'UNI-E-"+new['Employee_ID']+"'"+')"><i class="bi bi-card-list"></i></button>'
            else:
                edit_btn = ''
            new['Date_of_Joining'] = new['Date_of_Joining'][:10]
    #        if r.Name in existing_users:
    #            account = ""
    #        else:
    #            account = '<a href="/add_employee_account/'+str(new['id'])+'"><button  class="btn btn-info si">Sign Up</button></a>'
            new["edit"] = "<div style='display:flex;'>"+edit_btn+"</div>"
            data.append(new)
    else:
        for r in db.session.query(Employees).filter(Employees.created_by == current_user.username):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            if current_user.edit == True:
                edit_btn =  '<a href="/edit_employee/'+str(new['id'])+'"><button  class="btn btn-primary si"><i class="bi bi-pen"></i></button></a><a  href="/delete_employee/'+str(new['id'])+'"><button class="btn btn-danger si"><i class="bi bi-trash"></i></button></a>'
            else:
                edit_btn = ''
            new['Date_of_Joining'] = new['Date_of_Joining'][:10]
    #        if r.Name in existing_users:
    #            account = ""
    #        else:
    #            account = '<a href="/add_employee_account/'+str(new['id'])+'"><button  class="btn btn-info si">Sign Up</button></a>'
            new["edit"] = "<div style='display:flex;'>"+edit_btn+"</div>"
            data.append(new)
    f = open('employee_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('employees.html', data = data , columns = columns, user=current_user)



@handleemployees.route('/add_employee/', methods = ['GET','POST'])
@login_required
def add_employee():
    if current_user.hr == False:
        return abort(404)  
    form = AddEmployeeForm()
    if request.method == 'POST':
        #Status = form.Status.data
        Employee_Status = form.Employee_Status.data
        Employee_ID = form.Employee_ID.data
        Name = form.Name.data
        Position = form.Position.data
        Nationality = form.Nationality.data
        #UID = form.UID.data
        Date_of_Birth = form.Date_of_Birth.data
        Date_of_Joining = form.Date_of_Joining.data
        Emirates_ID = form.Emirates_ID.data
        #Card_No = form.Card_No.data
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
        crm_username = form.crm_username.data
        pers_no = form.pers_no.data
        company_email = form.company_email.data
        salary = form.salary.data
        slab = form.slab.data
        created_by = current_user.username
        created_date = datetime.now()+timedelta(hours=4)
        updated_date = datetime.now()+timedelta(hours=4)
        employee = Employees(created_by = created_by,  Employee_Status = Employee_Status,  Employee_ID = Employee_ID,  Name = Name,  Position = Position,  Nationality = Nationality,  Date_of_Birth = Date_of_Birth,  Date_of_Joining = Date_of_Joining,  Emirates_ID = Emirates_ID,  Emirates_Card_Expiry = Emirates_Card_Expiry,  Mobile_No = Mobile_No,  MOL_Personal_No = MOL_Personal_No,  Labor_Card_No = Labor_Card_No,  Labor_Card_Expiry = Labor_Card_Expiry,  Insurance_No = Insurance_No,  Insurance_Effective_Date = Insurance_Effective_Date,  Insurance_Expiry_Date = Insurance_Expiry_Date,  Date_of_Submission = Date_of_Submission,  Residence_Expiry = Residence_Expiry,  Remarks = Remarks, crm_username = crm_username, pers_no = pers_no, company_email = company_email, salary = salary, slab = slab, created_date = created_date, updated_date = updated_date)
        db.session.add(employee)
        db.session.commit()
        db.session.refresh(employee)
        employee_no = "E-"+Employee_ID

        try:
            document = secure_filename(form.profile_photo.data.filename)
            directory = UPLOAD_FOLDER+'/'+employee_no
            if not os.path.isdir(directory):
                os.mkdir(directory)
            form.profile_photo.data.save(os.path.join(directory, document))
            employee.profile_photo = ('/static/uploads02'+'/'+employee_no+"/"+document)
        except:
            employee.profile_photo = ""

        db.session.commit()
        additional_details('UNI-E-' + str(Employee_ID))
        print("here")
        return redirect(url_for('handleemployees.display_employees'))
    return render_template('add_employee.html', form=form, user = current_user.username, radio_enable = 'disabled', old_pics = '')
   
@handleemployees.route('/edit_employee/<var>', methods = ['GET','POST'])
@login_required
def edit_employee(var):
    if current_user.hr == False or current_user.edit == False:
        return abort(404) 
    edit = db.session.query(Employees).filter_by(id = var).first()
    form = AddEmployeeForm(obj = edit)
    old_pics = edit.profile_photo
    if request.method == 'POST':
        form.populate_obj(edit)
        edit.updated_date = datetime.now()+timedelta(hours=4)
        employee_no = "E-"+edit.Employee_ID
        try:
            document = secure_filename(form.profile_photo.data.filename)
            directory = UPLOAD_FOLDER+'/'+employee_no
            if not os.path.isdir(directory):
                os.mkdir(directory)
            form.profile_photo.data.save(os.path.join(directory, document))
            edit.profile_photo = ('/static/uploads02'+'/'+employee_no+"/"+document)
        except:
            pass
        db.session.commit()
        return redirect(url_for('handleemployees.display_employees'))
    return render_template('add_employee.html',form=form, radio_enable = 'enabled', old_pics = old_pics)


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
        all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).all()
    elif current_user.job_title == "Manager" and current_user.abudhabi == True:
        for r in db.session.query(Exitform).filter(Exitform.branch == 'Abu Dhabi'):
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
        all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).filter(User.abudhabi == True).all()
    elif current_user.job_title == "Manager" and current_user.dubai == True:
        for r in db.session.query(Exitform).filter(Exitform.branch == 'Dubai'):
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
        all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).filter(User.dubai == True).all()
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
        all_users = ''
    f = open('exitform_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
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
        branch = form.branch.data
        newexitform = Exitform(name=name, designation=designation, department=department, reason=reason, viewing_lead=viewing_lead, remarks=remarks, date_from=date_from, date_to=date_to, time_from=time_from, time_to=time_to, hr_acknowledge=hr_acknowledge, created_date = created_date, updated_date = updated_date, created_by = created_by, manager_approval = manager_approval, hr_approval = hr_approval, branch = branch)

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
        all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).all()
    elif current_user.job_title == "Manager" and current_user.abudhabi == True:
        for r in db.session.query(Leaveform).filter(Leaveform.branch == 'Abu Dhabi'):
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
        all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).filter(User.abudhabi == True).all()
    elif current_user.job_title == "Manager" and current_user.dubai == True:
        for r in db.session.query(Leaveform).filter(Leaveform.branch == 'Dubai'):
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
        all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).filter(User.dubai == True).all()
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
        all_users = ''
    f = open('leaveform_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
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
        branch = form.branch.data

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
        newleaveform = Leaveform(name=name, designation=designation, department=department, reason=reason, remarks=remarks, date_from=date_from, date_to=date_to, hr_ack_date=hr_ack_date, manager_ack_date=manager_ack_date, created_date = created_date, updated_date = updated_date, created_by = created_by, manager_approval = manager_approval, hr_approval = hr_approval, employee_no=employee_no, joining_date=joining_date, leave_type=leave_type, no_of_days=no_of_days, leave_balance=leave_balance, branch = branch)

        db.session.add(newleaveform)
        db.session.commit()
        db.session.refresh(newleaveform)
        newleaveform.refno = 'L-F-'+str(newleaveform.id)

        try:
            document = secure_filename(form.docs.data.filename)
            directory = UPLOAD_FOLDER+'/'+newleaveform.refno
            if not os.path.isdir(directory):
                os.mkdir(directory)
            form.docs.data.save(os.path.join(directory, document))
            newleaveform.docs = ('/static/uploads02'+'/L-F-'+str(newleaveform.id)+"/"+document)
        except:
            newleaveform.docs = ""

        db.session.commit()

        return redirect(url_for('handleemployees.display_leaveforms'))
    return render_template('add_leaveform.html', form=form, user = current_user.username, radio_enable = 'disabled', old_docs = '')

@handleemployees.route('/edit_leaveform/<variable>', methods = ['GET','POST'])
@login_required
def edit_leaveform(variable):
    edit = db.session.query(Leaveform).filter_by(refno=variable).first()
    form = AddLeaveformentry(obj = edit)
    old_docs = edit.docs
    if request.method == 'POST':
        form.populate_obj(edit)
        edit.updated_date = datetime.now()+timedelta(hours=4)
        try:
            document = secure_filename(form.docs.data.filename)
            directory = UPLOAD_FOLDER+'/'+edit.refno
            if not os.path.isdir(directory):
                os.mkdir(directory)
            form.docs.data.save(os.path.join(directory, document))
            edit.docs = ('/static/uploads02'+'/L-F-'+str(edit.id)+"/"+document)
        except:
            pass
        db.session.commit()
        return redirect(url_for('handleemployees.display_leaveforms'))
    return render_template('add_leaveform.html', form=form, user = current_user.username, radio_enable = 'enabled', old_docs = old_docs)

@handleemployees.route('/delete_leaveform/<variable>', methods = ['GET','POST'])
@login_required
def delete_leaveform(variable):
    delete = db.session.query(Leaveform).filter_by(refno=variable).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('handleemployees.display_leaveforms'))


#Advance Request FORMS

@handleemployees.route('/human_resource/advance_forms',methods = ['GET','POST'])
@login_required
def display_advanceforms():
    if current_user.listing == False and current_user.sale == False:
        return abort(404)
    data = []
    if current_user.is_admin == True or current_user.job_title == "Accountant":
        for r in db.session.query(Advanceform).all():
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason', 'updated_date', 'designation']: new.pop(k)
            edit_btn = '<a href="/edit_advanceform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
            delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            new["edit"] = "<div style='display:flex;'>"+edit_btn+delete_btn+"</div>"
            new['request_date'] = new['request_date'][:10]
            data.append(new)
        all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).all()
    elif current_user.job_title == "Manager" and current_user.abudhabi == True:
        for r in db.session.query(Advanceform).filter(Advanceform.branch == 'Abu Dhabi'):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason']: new.pop(k)
            if new['ceo_approval'] == "Pending":
                edit_btn = '<a href="/edit_advanceform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
                delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            else:
                edit_btn = "Request Closed"
                delete_btn = ''
            new["edit"] = "<div style='display:flex;'>"+edit_btn+delete_btn+"</div>"
            new['request_date'] = new['request_date'][:10]
            data.append(new)
        all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).filter(User.abudhabi == True).all()
    elif current_user.job_title == "Manager" and current_user.dubai == True:
        for r in db.session.query(Advanceform).filter(Advanceform.branch == 'Dubai'):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason']: new.pop(k)
            if new['ceo_approval'] == "Pending":
                edit_btn = '<a href="/edit_advanceform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
                delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            else:
                edit_btn = "Request Closed"
                delete_btn = ''
            new["edit"] = "<div style='display:flex;'>"+edit_btn+delete_btn+"</div>"
            new['request_date'] = new['request_date'][:10]
            data.append(new)
        all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).filter(User.dubai == True).all()
    elif current_user.team_lead == True:
        for r in db.session.query(Advanceform).filter(Advanceform.created_by == current_user.username):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason']: new.pop(k)
            if new['manager_approval'] == "Pending":
                edit_btn = '<a href="/edit_advanceform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
                delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            else:
                edit_btn = "Request Closed"
                delete_btn = ''
            new["edit"] = "<div style='display:flex;'>"+edit_btn+delete_btn+"</div>"
            new['request_date'] = new['request_date'][:10]
            data.append(new)
        for i in current_user.team_members.split(','):
            for r in db.session.query(Advanceform).filter(Advanceform.created_by == i):
                row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
                new = row2dict(r)
                for k in ['reason']: new.pop(k)
                if new['manager_approval'] == "Pending":
                    edit_btn = '<a href="/edit_advanceform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
                    delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
                else:
                    edit_btn = "Request Closed"
                    delete_btn = ''
                new["edit"] = "<div style='display:flex;'>"+edit_btn+delete_btn+"</div>"
                new['request_date'] = new['request_date'][:10]
                data.append(new)
        all_users = db.session.query(User).filter(User.sale == True).filter(User.abudhabi == True).all()
    elif current_user.sale == True or current_user.listing == True or current_user.department == "Marketing":
        for r in db.session.query(Advanceform).filter(Advanceform.created_by == current_user.username):
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            for k in ['reason']: new.pop(k)
            if new['tl_approval'] == "Pending":
                edit_btn = '<a href="/edit_advanceform/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
            else:
                edit_btn = "Request Closed"
            new["edit"] = "<div style='display:flex;'>"+edit_btn+"</div>"
            new['request_date'] = new['request_date'][:10]
            data.append(new)
        all_users = ''
    f = open('advanceform_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('advance_forms.html', data = data , columns = columns, user = current_user.username, all_users = all_users)

@handleemployees.route('/add_advanceform', methods = ['GET','POST'])
@login_required
def add_advance_form(): 
    form = Addadvanceform()
    if request.method == 'POST': 
        name = form.name.data
        designation = form.designation.data
        department = form.department.data
        employee_no = form.employee_no.data
        request_date = form.request_date.data
        com_from = form.com_from.data
        amount_requested = form.amount_requested.data
        salary_month = form.salary_month.data
        reason = form.reason.data
        branch = form.branch.data

        tl_ack = form.tl_ack.data
        if form.tl_approval.data != None:
            tl_approval = form.tl_approval.data
        else:
            tl_approval = 'Pending'

        manager_ack = form.manager_ack.data
        if form.manager_approval.data != None:
            manager_approval = form.manager_approval.data
        else:
            manager_approval = 'Pending'

        ceo_ack = form.ceo_ack.data
        if form.ceo_approval.data != None:
            ceo_approval = form.ceo_approval.data
        else:
            ceo_approval = 'Pending'

        account_ack = form.account_ack.data
        if form.account_approval.data != None:
            account_approval = form.account_approval.data
        else:
            account_approval = 'Pending'

        remarks = form.remarks.data
        created_date = datetime.now()+timedelta(hours=4)
        updated_date = datetime.now()+timedelta(hours=4)
        created_by = current_user.username
        newadvanceform = Advanceform(name=name,designation=designation,department=department,request_date=request_date,amount_requested=amount_requested,salary_month=salary_month,reason=reason,remarks=remarks,created_date=created_date,updated_date=updated_date,created_by=created_by,manager_ack=manager_ack,manager_approval=manager_approval,employee_no=employee_no,tl_ack=tl_ack,tl_approval=tl_approval,ceo_ack=ceo_ack,ceo_approval=ceo_approval,account_ack=account_ack,account_approval=account_approval,com_from=com_from, branch = branch)

        db.session.add(newadvanceform)
        db.session.commit()
        db.session.refresh(newadvanceform)
        newadvanceform.refno = 'CAR-F-'+str(newadvanceform.id)
        db.session.commit()

        return redirect(url_for('handleemployees.display_advanceforms'))
    return render_template('add_advanceform.html', form=form, user = current_user.username)


@handleemployees.route('/edit_advanceform/<variable>', methods = ['GET','POST'])
@login_required
def edit_advanceform(variable):
    edit = db.session.query(Advanceform).filter_by(refno=variable).first()
    form = Addadvanceform(obj = edit)
    if request.method == 'POST':
        form.populate_obj(edit)
        edit.updated_date = datetime.now()+timedelta(hours=4)
        db.session.commit()
        return redirect(url_for('handleemployees.display_advanceforms'))
    return render_template('add_advanceform.html', form=form, user = current_user.username)

@handleemployees.route('/delete_advanceform/<variable>', methods = ['GET','POST'])
@login_required
def delete_advanceform(variable):
    delete = db.session.query(Advanceform).filter_by(refno=variable).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('handleemployees.display_advanceforms'))