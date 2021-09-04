import email
from operator import and_
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms import BooleanField, StringField, PasswordField, validators, IntegerField, FileField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.widgets import HiddenInput
from flask_wtf import FlaskForm
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from flask_admin import Admin
import os 
import sqlite3
from handlecontacts import handlecontacts
from handleproperties import handleproperties
from handleleads import handleleads
from handledeals import handledeals
from handlestorage import handlestorage
from portals import portals
from models import *
import json
from forms import *
from apscheduler.schedulers.background import BackgroundScheduler
from functions import *
from sqlalchemy import or_
import io 
import csv
from logging import FileHandler, WARNING

def assign_lead(lead,contact_refno):
    print('lead for ' + lead['refno'])
    p = db.session.query(Properties).filter_by(refno=lead['refno']).first()
    newlead = Leads(type="secondary",locationtext=p.locationtext,building=p.building,subtype=p.subtype,min_beds=p.bedrooms,min_price=p.price,contact_name=lead['contact_name'],contact_number=lead['contact_number'],contact_email=lead['contact_email'],contact = contact_refno,property_requirements=lead['refno'])
    db.session.add(newlead)
    db.session.commit()
    db.session.refresh(newlead)
    newlead.refno = 'UNI-L-'+str(newlead.id)
    db.session.commit()
    notes('UNI-L-' + str(newlead.id))
    
def lead_contact(lead):
    name = lead['contact_name']
    name = name.split(' ')
    first_name = name[0]
    last_name = ''.join(name[1:])
    number = lead['contact_number']
    email = lead['contact_email']
    con_test = db.session.query(Contacts).filter_by(number=number,email=email).first()
    con = bool(con_test)
    if con == False:
        newcontact = Contacts(first_name=first_name, last_name=last_name ,number=number,email=email)
        db.session.add(newcontact)
        db.session.commit()
        db.session.refresh(newcontact)
        newcontact.refno = 'UNI-O-'+str(newcontact.id)
        db.session.commit()
        return newcontact.refno
    elif con == True:
        return con_test.refno

def task():
    lead = get_lead()
    global email_lead
    h_lead = hash(str(lead))
    print('ok')
    if email_lead != h_lead:
        email_lead = h_lead
        contact_refno = lead_contact(lead)
        assign_lead(lead, contact_refno)
   
def assign():
    availableLeads = [lead.refno for lead in db.session.query(Leads).filter_by(agent = None).all()]
    availableagents = [user.username for user in db.session.query(User).filter_by(schedule = True).all()]
    assigned, no_follow_up = getAvailableAgents(availableagents, availableLeads)   
    if not assigned:
        pass
    else:
        print(assigned)
        for i in assigned:
            e = db.session.query(Leads).filter_by(refno = i[0]).first()
            e.agent = i[1]
            e.status = 'Open'
            e.sub_status = 'In progress'
            db.session.commit()
            logs(i[1],i[0],'Added')
    if not no_follow_up:
        pass
    else:
        reassignAgents(no_follow_up)

def reassignAgents(x):
    for i in x:
        e = db.session.query(Leads).filter_by(refno = i[0]).first()
        e.agent = None
        e.status = 'Open'
        e.sub_status = 'In progress'
        db.session.commit()
        update_lead_note(i[1],i[0],'Lost','Open','In progress')
        logs(i[1],i[0],'Lost')
        lost_lead(i[1],i[0])

sched = BackgroundScheduler(daemon=True)
sched.add_job(task,'cron', minute='*/1',hour='*', id='addLead')
sched.add_job(assign,'cron', second='*/20',  minute='*',hour='*',id='assignLead')


app = Flask(__name__, template_folder = 'template')
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)
app.logger.addHandler(file_handler)
app.register_blueprint(handlecontacts)
app.register_blueprint(handleproperties)
app.register_blueprint(handleleads)
app.register_blueprint(handledeals)
app.register_blueprint(handlestorage)
app.register_blueprint(portals)
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+os.getcwd()+'/test.db'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db = SQLAlchemy(app)
admin = Admin(app,template_mode='bootstrap3')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
Bootstrap(app) 
email_lead = ''



class AddUserForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25), validators.DataRequired()])
    password = StringField('Password', [validators.DataRequired()])
    number = IntegerField('Contact Number', [validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=4, max=80),validators.DataRequired()])
    job_title = StringField('Job Title', [validators.Length(min=4, max=25), validators.DataRequired()])
    department = StringField('Department', [validators.Length(min=4, max=25), validators.DataRequired()])
    

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(50))
    number = db.Column(db.Integer)
    job_title = db.Column(db.String(50))
    department = db.Column(db.String(50))
    profile_picture = db.Column(db.String())
    is_admin = db.Column(db.Boolean, default=False)
    listing = db.Column(db.Boolean, default=False)
    sale = db.Column(db.Boolean, default=False)
    deal = db.Column(db.Boolean, default=False)
    hr = db.Column(db.Boolean, default=False)
    contact = db.Column(db.Boolean, default=False)
    edit = db.Column(db.Boolean, default=False)
    viewall = db.Column(db.Boolean, default=False)
    export = db.Column(db.Boolean, default=False)
    schedule = db.Column(db.Boolean, default=False)


class Controller(ModelView):
    def is_accessible(self):
        if current_user.is_admin == True:
            return current_user.is_authenticated
        else:
            return abort(404)
    def not_auth(self):
        return "Not Permitted"

class UserView(ModelView):
    create_template = 'create_user.html'
    def is_accessible(self):
        if current_user.is_admin == True:
            return current_user.is_authenticated
        else:
            return abort(404)

admin.add_view(Controller(Properties, db.session))
admin.add_view(Controller(Leads, db.session))
admin.add_view(Controller(Deals, db.session))
admin.add_view(Controller(Contacts, db.session))
admin.add_view(UserView(User, db.session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/', methods = ['GET','POST'])
def login():
    form = LoginForm()
    
    if request.method == 'POST':
        username_ = form.username.data
        password_ = form.password.data
        user = User.query.filter_by(username=username_).first()
        print('sign in')
        if user:
            if check_password_hash(user.password, password_):
                login_user(user)
                return redirect(url_for('dashboard'))
      
    return render_template('login.html', form=form)

@app.route('/user_obj')
def user_obj():
    return current_user.id

@app.route('/add_user', methods = ['GET','POST'])
@login_required
def add_user(): 
    form = AddUserForm()
    if request.method == 'POST': 
        passer = generate_password_hash(form.password.data,method='sha256')
        uploaded_file = request.files['file']
        dir = ''
        if uploaded_file.filename != '':
            extension = os.path.splitext(uploaded_file.filename)[1]
            uploaded_file.filename = form.username.data + extension
            uploaded_file.save(os.getcwd() + '/static/userdata/'+uploaded_file.filename)
            dir = str('/static/userdata/'+uploaded_file.filename)
        newuser = User(username=form.username.data, password=passer, number=form.number.data, email = form.email.data, job_title = form.job_title.data, department = form.department.data, profile_picture = dir)
        db.session.add(newuser)
        db.session.commit()
        create_json(form.username.data)
        logs(form.username.data,form.username.data,"Created")
        return redirect('/admin/user/')
    return render_template('create_user.html', form=form)


@app.route('/dashboard', methods = ['GET','POST'])
@login_required
def dashboard(): 
    if request.method == 'POST':   
        user_reminders = reminders(current_user.username)
        return jsonify({'data' : user_reminders})
    user_reminders = reminders(current_user.username)
    return render_template('dashboard.html', user = current_user, reminders = user_reminders)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return(redirect(url_for('login')))

@app.route('/all_contacts',methods = ['GET','POST'])
@login_required
def all_contacts():
    get_contacts = db.session.query(Contacts).all()
    all_contacts = []
    for contact in get_contacts:
        contactObj = {}
        contactObj['refno'] = contact.refno
        contactObj['name'] = str(contact.first_name + ' ' + contact.last_name)
        contactObj['contact'] = contact.number
        contactObj['email'] = contact.email
        contactObj['nationality'] = contact.nationality
        all_contacts.append(contactObj)
    return jsonify({'all_contacts':all_contacts})

@app.route('/all_logs/<var>',methods = ['GET','POST'])
@login_required
def all_logs(var):
    user_log = get_log(var)
    all_logs = []
    for i in user_log:
        logObj = {}
        logObj['date'] = i['date']
        logObj['time'] = i['time']
        logObj['ref'] = i['ref']
        logObj['task'] = i['task']
        all_logs.append(logObj)
    return jsonify({'all_logs':all_logs})

@app.route('/post_reminder/<fd>/<td>/<ft>/<tt>/<title>',methods = ['GET','POST'])
@login_required
def post_reminder(fd,td,ft,tt,title):
    post_reminders(current_user.username,fd,td,ft,tt,title)
    return jsonify(success=True)

@app.route('/scheduler/<var>')
def scheduler(var):
    if var == 'start':
        if sched.state == 0:
            sched.start()
    if var == 'stop':
        sched.shutdown()
    if var == 'state':
        return str(sched.state)
    return render_template('admin/index.html', state = str(sched.state))

@app.route('/scheduler/update/<var>')
def scheduler_update(var):
    update_sch(var)
    return render_template('admin/index.html', state = str(sched.state))

@app.route('/all_users',methods = ['GET','POST'])
@login_required
def all_users():
    get_users = db.session.query(User).all()
    all_users = []
    for contact in get_users:
        userObj = {}
        userObj['name'] = contact.username
        userObj['number'] = contact.number
        userObj['email'] = contact.email
        all_users.append(userObj)
    return jsonify({'all_users':all_users})

@app.route('/all_users_commission/<variable>/<type>',methods = ['GET','POST'])
@login_required
def all_users_commission(variable, type):
    get_user = db.session.query(User).filter_by(username = variable).first()
    all_deals = db.session.query(Deals).filter(or_(Deals.agent_1 == variable,Deals.agent_2 == variable))
    total_deal = 0
    count = 0
    for deal in all_deals:
        count = count+1
        total_deal = int(deal.deal_price) + total_deal
    if get_user.listing == True and count >= 3:
        commission = get_commission("list", total_deal, type)
    elif get_user.sale == True:
        commission = get_commission("sale", total_deal, type)
    return jsonify({'commission':commission})

@app.route('/all_properties',methods = ['GET','POST'])
@login_required
def all_properties():
    get_properties = db.session.query(Properties).all()
    all_properties = []
    for property in get_properties:
        a = property
        propertyObj = vars(a)
        propertyObj.pop('_sa_instance_state')
        all_properties.append(propertyObj)
    return jsonify({'all_properties':all_properties})

@app.route('/all_properties/<variable>',methods = ['GET','POST'])
@login_required
def view_properties(variable):
    property = db.session.query(Properties).filter_by(refno = variable).first()
    all_property = []
    propertyObj = {}
    propertyObj = vars(property)
    propertyObj.pop('_sa_instance_state')
    a=property.photos.split('|')
    if a[1:] == '':
        propertyObj['photos'] = a[1:]
    else:
        propertyObj['photos'] = a
    all_property.append(propertyObj)
    return jsonify({'property':all_property})

@app.route('/all_leads',methods = ['GET','POST'])
@login_required
def all_leads():
    get_lead = db.session.query(Leads).all()
    all_leads = []
    for lead in get_lead:
        a = lead
        leadObj = vars(a)
        leadObj.pop('_sa_instance_state')
        all_leads.append(leadObj)
    return jsonify({'all_leads':all_leads})

@app.route('/all_leads/<variable>',methods = ['GET','POST'])
@login_required
def view_leads(variable):
    lead = db.session.query(Leads).filter_by(refno = variable).first()
    all_lead = []
    leadObj = {}
    leadObj = vars(lead)
    leadObj.pop('_sa_instance_state')
    all_lead.append(leadObj)
    return jsonify({'lead':all_lead})

@app.route('/all_count',methods = ['GET','POST'])
@login_required
def all_count():
    user_listing = Properties.query.filter_by(assign_to = current_user.username).count()
    all_listing = db.session.query(Properties).count()
    user_leads = Leads.query.filter_by(agent = current_user.username).count()
    all_leads = db.session.query(Leads).count()
    all_count = []
    countObj = {}
    countObj['ulist'] = user_listing
    countObj['alist'] = all_listing
    countObj['ulead'] = user_leads
    countObj['alead'] = all_leads
    all_count.append(countObj)
    return jsonify({'all_count':all_count})

@app.route('/all_notes/<variable>',methods = ['GET','POST'])
@login_required
def view_notes(variable):
    notes = get_notes(variable)
    all_notes = []
    if 'l' in variable.lower():
        for i in notes:
            noteObj = {}
            noteObj['date'] = i['date']
            noteObj['time'] = i['time']
            noteObj['user'] = i['user']
            noteObj['comment'] = i['comment']
            noteObj['status'] = i['status']
            noteObj['substatus'] = i['substatus']
            all_notes.append(noteObj)
    else:
        for i in notes:
            noteObj = {}
            noteObj['date'] = i['date']
            noteObj['time'] = i['time']
            noteObj['user'] = i['user']
            noteObj['comment'] = i['comment']
            all_notes.append(noteObj)
    return jsonify({'notes': all_notes})

@app.route('/post_note/<list_id>/<com>',methods = ['GET','POST'])
@login_required
def post_note(list_id,com):
    update_note(current_user.username,list_id,com)
    return jsonify(success=True)

@app.route('/post_lead_note/<list_id>/<com>/<status>/<substatus>',methods = ['GET','POST'])
@login_required
def post_lead_note(list_id,com,status,substatus):
    a = db.session.query(Leads).filter_by(refno = list_id).first()
    a.sub_status = substatus
    a.status = status
    db.session.commit()
    update_lead_note(current_user.username,list_id,com,status,substatus)
    update_user_note(current_user.username,list_id,status,substatus)
    return jsonify(success=True)

@app.route('/follow_up/<list_id>/<com>',methods = ['GET','POST'])
@login_required
def follow_up(list_id,com):
    a = db.session.query(Leads).filter_by(refno = list_id).first()
    a.status = "Open"
    a.sub_status = "Follow up"
    db.session.commit()
    update_lead_note(current_user.username,list_id,com,"Open","Follow up")
    update_user_note(current_user.username,list_id,"Open","Follow up")
    return jsonify(success=True)

@app.route('/chart/<chart>/<user>',methods = ['GET','POST'])
@login_required
def gen_chart(chart,user):
    labels,data,bg,bd,t = chart_data(chart,user)
    if t == 'bar':
        chartObj = {}
        chartObj['labels'] = labels
        chartObj['data'] = data
        chartObj['bg'] = bg
        chartObj['bd'] = bd
    elif t == 'lead':
        chartObj = {}
        chartObj['labels'] = labels
        chartObj['data'] = data[0]
        chartObj['data2'] = data[1]
        chartObj['bg'] = bg
        chartObj['bd'] = bd
    elif t == 'list':
        chartObj = {}
        chartObj['labels'] = labels
        chartObj['data'] = data
        chartObj['bg'] = bg
        chartObj['bd'] = bd
    return jsonify({'chart': chartObj})

@app.route('/export/<type>/<data>',methods = ['GET','POST'])
@login_required
def export(type,data):
    print(type)
    if type == "leads":
        type = Leads
    elif type == "properties":
        type = Properties
    elif type == "deals":
        type = Deals 
    ref = data.split(',')
    Obj = db.session.query(type).all()
    output = io.StringIO()
    writer = csv.writer(output)
    i = []
    for r in Obj:
        if r.refno in ref:
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            z =  list(new.values())
            nl = []
            for y in z:
                if y == '':
                    nl.append('None')
                else:
                    nl.append(y)
            row = (',').join(c.replace(',','-') for c in nl)
            i.append(row)
    

    header = list(new.keys())
    writer.writerow(header)
    for x in i:
        writer.writerow(x.split(','))
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=report.csv"})

if __name__ == '__main__':
    app.run(debug = True)



'''
passer = generate_password_hash('ahmedrauf',method='sha256')
newuser = User(username='ahmed', password=passer, number=5017656756, email = 'cool@gmail.com',is_admin = True)
db.session.add(newuser)
db.session.commit()


passer = generate_password_hash('ahmedrauf',method='sha256')
newuser = User(username='ahmed2', password=passer, number=5017656756, email = 'cool@gmail.com')
db.session.add(newuser)
db.session.commit()
'''
