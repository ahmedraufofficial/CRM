from curses.ascii import NUL
from operator import methodcaller
from xml.dom.minicompat import EmptyNodeList
from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask.globals import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import except_all
from models import Leads, Properties,Contacts, User, Deals, Transactionad
from forms import Addtransactionad
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import date, datetime,time
from sqlalchemy import or_,and_,desc,func
import csv
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth(scheme='Bearer')
tokens = {
    ''
}

NOTES = os.getcwd() + '/static/notes'

db = SQLAlchemy()
handleadmin = Blueprint('handleadmin', __name__, template_folder='templates')

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return token

@handleadmin.route('/fetch_txn_token',methods = ['GET','POST'])
@login_required
def fetch_txn_token():
    return(jsonify(''))

#@handleadmin.route('/admin/listing',methods = ['GET','POST'])
#@login_required
#def display_listing_admin():
#    if current_user.is_admin == False:
#        return abort(404)   
#    props_10 = db.session.query(Properties.locationtext, func.count(Properties.locationtext).filter(Properties.status == "Available").label('count')).group_by(Properties.locationtext).order_by(desc('count')).limit(7).all()
#    coms_10 = db.session.query(Properties.building, func.count(Properties.building).filter(Properties.status == "Available").label('count')).group_by(Properties.building).order_by(desc('count')).limit(7).all()
#    listing_agents = [User.username for User in db.session.query(User).filter_by(job_title = 'Listing Agent').all()]
#    analysis = {}
#    for i in listing_agents:
#        total_available_props = [Properties.assign_to for Properties in db.session.query(Properties).filter(and_(Properties.assign_to == i, Properties.status == 'Available')).all()]
#        analysis[i] = len(total_available_props)
#    print(analysis)
#    return render_template('admin_dash.html', props_10 = props_10, coms_10 = coms_10)
    
@handleadmin.route('/admin-profiles')
@login_required
def admins_dash():
    sum_keys = ['deal_price', 'gross_commission', 'amount_received', 'amount_eligible', 'agent_received', 'agent_pending', 'agent_commission', 'pending_eligible', 'ct_value', 'kickback_amount', 'commission_agent_2']
    editable_keys = ['agent_pers_comm']
    f = open('accounts_headers.json')
    columns = json.load(f)
    col = columns["headers"]
    all_sale_users = db.session.query(User).filter_by(sale = True).all()
    return render_template('accounts_dash.html', user = current_user.username, data = '', columns = col, sum_keys=sum_keys, editable_keys = editable_keys, all_sale_users = all_sale_users)

@handleadmin.route('/fetch_transactions')
@auth.login_required
def fetch_txns():
    query = db.session.query(Deals)
    conditions = []
    filters_01 = {key: request.args.get(key) for key in request.args}
    filters = {key: filters_01[key] for key in ['propdate', 'propdate2'] if key in filters_01}
    for key, value in filters.items():
        if key == 'propdate':
            conditions.append(Deals.actual_deal_date >= value)
        elif key == 'propdate2':
            value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
            value_as_datetime += timedelta(days=1)
            value = value_as_datetime.strftime('%Y-%m-%d')
            conditions.append(Deals.actual_deal_date <= value)
        else:
            conditions.append(getattr(Leads, key) == value)
    query = query.filter(and_(*conditions))

    deals = []
    for r in query.filter(Deals.agent_1 == filters_01['agent_1']):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        for k in ['contact_buyer_number','contact_buyer_name','contact_buyer','listing_ref','created_by','type','id','transaction_type','source','priority','deposit','agency_fee_seller','agency_fee_buyer','include_vat','split_with_external_referral','agent_2','estimated_deal_date','unit_category','unit_beds','unit_floor','unit_type','buyer_type','finance_type','tenancy_start_date','tenancy_renewal_date','cheques', 'contact_buyer_email','contact_seller','contact_seller_name','contact_seller_number','contact_seller_email', 'status','sub_status','hot_lead','deal_type','bank_representative_name','bank_representative_mobile','referral_date','pre_approval_loan','down_payment_available','down_payment','number_cheque_payment','cheque_payment_type','move_in_date','client_referred_bank','loan_amount','project','floor_no','plot_size','unit_price','percentage','amount']: new.pop(k, None)
        new['actual_deal_date'] = new['actual_deal_date'][:10]
        try:
            if float(str(new['gross_commission'].replace(',', ''))) > float(str(new['total_commission'].replace(',', ''))):
                new['gross_commission'] = new['total_commission']
            else:
                pass
        except:
            pass
        new['options'] = ("<button class='btn-warning si2' style='color:white; background-color: red !important;' data-toggle='modal' data-target='#ctmodal' ""onclick=\"calculate_ct('{}')\"><i class='bi bi-calculator'></i></button>"+"<button class='btn-warning si2' style='color:white;' data-toggle='modal' data-target='#TxnModal' ""onclick=\"view_txn('{}')\"><i class='bi bi-journal-text'></i></button>").format(new['refno'], new['refno'])
        deals.append(new)
    sum_keys = ['deal_price', 'gross_commission', 'amount_received', 'amount_eligible', 'agent_received', 'agent_pending', 'agent_commission', 'pending_eligible', 'ct_value', 'kickback_amount', 'commission_agent_2']
    editable_keys = ['agent_pers_comm']
    f = open('accounts_headers.json')
    columns = json.load(f)
    col = columns["headers"]
    return jsonify(data=deals, columns = col, sum_keys=sum_keys, editable_keys = editable_keys)

@handleadmin.route('/save_edited_deals', methods = ['GET','POST'])
@login_required
def save_edited_deals():
    table_data = request.json.get('data')
    for row in table_data:
        deal = db.session.query(Deals).filter(Deals.refno == row['refno']).first()
        deal.agent_pers_comm = row['agent_pers_comm']
        deal.agent_commission = row['agent_commission']
    db.session.commit()
    return jsonify({"status": "success"})

@handleadmin.route('/add_transaction_ad', methods = ['GET','POST'])
@login_required
def add_transaction():
    if current_user.hr == False or current_user.abudhabi == False:
        return abort(404) 
    form = Addtransactionad()
    if request.method == 'POST': 
        Session = sessionmaker(bind=db.get_engine(bind='third'))
        session = Session()
        user = form.user.data
        deal_ref = form.deal_ref.data
        transaction_date = form.transaction_date.data
        type = form.type.data
        mode = form.mode.data
        amount = form.amount.data
        description = form.description.data
        created_by = current_user.username
        created_date = datetime.now()+timedelta(hours=4)
        x = recalculatemyg(deal_ref, user, type, amount)
        newtransaction = Transactionad(user=user,deal_ref=deal_ref,transaction_date=transaction_date,type=type,mode=mode,amount=amount,description=description,created_by=created_by,created_date=created_date)
        session.add(newtransaction)
        session.commit()
        session.refresh(newtransaction)
        newtransaction.refno = 'UNI-T-'+str(newtransaction.id)
        session.commit()
        session.close()
        return redirect(url_for('handleadmin.admins_dash'))
    return render_template('add_transaction.html', form=form, user = current_user.username)

def recalculatemyg(deal_ref, user, type, amount):
    deal = db.session.query(Deals).filter(and_(Deals.refno == deal_ref),(Deals.agent_1 == user)).first()

    if deal.agent_pers_comm == '' or  deal.agent_pers_comm == None:
        raise ValueError("The Agent Commision Percentage is missing or empty.")
    
    if deal.agent_received == '' or deal.agent_received == None:
        deal.agent_received = '0'

    if deal.amount_received == '' or deal.amount_received == None:
        deal.amount_received = '0'

    if deal.kickback_amount != '' and deal.kickback_amount != None:
        kickback = float(deal.kickback_amount.replace(',', ''))
    else:
        kickback = 0

    if deal.commission_agent_2 != '' and deal.commission_agent_2 != None:
        listing_comm = float(deal.commission_agent_2.replace(',', ''))
    else:
        listing_comm = 0

    if type == 'To company':
        w = float(deal.amount_received.replace(',', '')) + float(amount.replace(',', ''))
        deal.amount_received = f"{w:,.2f}"
        x = ((float(deal.amount_received.replace(',', ''))- kickback - listing_comm) * (float(deal.agent_pers_comm) / 100))
        deal.amount_eligible = f"{x:,.2f}"
        y = float(deal.amount_eligible.replace(',', '')) - float(str(deal.agent_received).replace(',', ''))
        deal.pending_eligible = f"{y:,.2f}"
        db.session.commit()

    elif type == 'To agent':
        w = float(str(deal.agent_received).replace(',', '')) + float(amount.replace(',', ''))
        deal.agent_received = f"{w:,.2f}"
        x = float(str(deal.amount_eligible).replace(',', '')) - float(deal.agent_received.replace(',', ''))
        deal.pending_eligible = f"{x:,.2f}"
        y = float(deal.agent_commission.replace(',', '')) - float(deal.agent_received.replace(',', ''))
        deal.agent_pending = f"{y:,.2f}"
        db.session.commit()

    else:
        raise ValueError("Please contact IT.")
    

@handleadmin.route('/view_txns/<refno>', methods = ['GET','POST'])
@login_required
def view_transactions(refno):
    Session = sessionmaker(bind=db.get_engine(bind='third'))
    session = Session()
    txns = session.query(Transactionad).filter(Transactionad.deal_ref == refno)
    all_txns = []
    for i in txns:
        noteObj = {}
        noteObj['refno'] = i.refno
        noteObj['type'] = i.type
        noteObj['transaction_date'] = i.transaction_date.strftime("%d %b %Y")
        noteObj['mode'] = i.mode
        noteObj['amount'] = i.amount
        all_txns.append(noteObj)
    session.close()
    return jsonify({'txns': all_txns})

@handleadmin.route('/calculate_ct/<refno>', methods = ['GET','POST'])
@login_required
def calculate_ct(refno):
    query = db.session.query(Deals).filter(Deals.refno == refno).first()
    try:
        if float(str(query.gross_commission.replace(',', ''))) > float(str(query.total_commission.replace(',', ''))):
            x = float(str(query.total_commission.replace(',', '')))
        else: 
            x = float(str(query.gross_commission.replace(',', '')))
    except:
        x = float(str(query.total_commission.replace(',', '')))
    w = x * 0.09
    query.ct_percentage = f"{w:,.2f}"
    z = x - w
    query.ct_value = f"{z:,.2f}"
    db.session.commit()
    return redirect(url_for('handleadmin.admins_dash'))



# Sales Report (BIG - TIME)

@handleadmin.route('/accounts_summary')
@login_required
def accounts_summary():
    sum_keys = ['deal_price', 'gross_commission', 'amount_received', 'ct_value', 'ct_percentage', 'gross_profit', 'kickback_amount', 'commission_agent_2', 'agent_commission']
    f = open('accounts_headers.json')
    columns = json.load(f)
    col = columns["big_headers"]
    all_sale_users = db.session.query(User).filter_by(sale = True).all()
    return render_template('accounts_summary.html', user = current_user.username, data = '', columns = col, sum_keys=sum_keys, all_sale_users = all_sale_users)

@handleadmin.route('/fetch_summary')
@auth.login_required
def fetch_summary():
    query = db.session.query(Deals)
    conditions = []
    filters_01 = {key: request.args.get(key) for key in request.args}
    filters = {key: filters_01[key] for key in ['propdate', 'propdate2'] if key in filters_01}
    for key, value in filters.items():
        if key == 'propdate':
            conditions.append(Deals.actual_deal_date >= value)
        elif key == 'propdate2':
            value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
            value_as_datetime += timedelta(days=1)
            value = value_as_datetime.strftime('%Y-%m-%d')
            conditions.append(Deals.actual_deal_date <= value)
        else:
            pass
    query = query.filter(and_(*conditions))

    deals = []
    for r in query:
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        for k in ['contact_buyer_number','contact_buyer','listing_ref','created_by','id','source','priority','deposit','agency_fee_seller','agency_fee_buyer','include_vat','split_with_external_referral','estimated_deal_date','unit_category','unit_beds','unit_floor','unit_type','buyer_type','finance_type','tenancy_start_date','tenancy_renewal_date','cheques', 'contact_buyer_email','contact_seller','contact_seller_name','contact_seller_number','contact_seller_email', 'status','sub_status','hot_lead','deal_type','bank_representative_name','bank_representative_mobile','referral_date','pre_approval_loan','down_payment_available','down_payment','number_cheque_payment','cheque_payment_type','move_in_date','client_referred_bank','loan_amount','project','floor_no','plot_size','unit_price','percentage','amount']: new.pop(k, None)
        new['actual_deal_date'] = new['actual_deal_date'][:10]
        try:
            if float(str(new['gross_commission'].replace(',', ''))) > float(str(new['total_commission'].replace(',', ''))):
                new['gross_commission'] = new['total_commission']
            else:
                pass
        except:
            pass

        kickback = safe_float(new['kickback_amount'])
        agent = safe_float(new['agent_commission'])
        listing = safe_float(new['commission_agent_2'])

        if new['ct_value'] != '' and new['ct_value'] != 'None':
            x = float(str(new['ct_value']).replace(',', '')) - kickback - agent - listing
        else:
            x = float(str(new['gross_commission']).replace(',', '')) - kickback - agent - listing

        new['gross_profit'] = f"{x:,.2f}"
        new['options'] = ("<button class='btn-warning si2' style='color:white;' data-toggle='modal' data-target='#TxnModal' ""onclick=\"view_txn('{}')\"><i class='bi bi-journal-text'></i></button>").format(new['refno'])
        deals.append(new)
    sum_keys = ['deal_price', 'gross_commission', 'amount_received', 'ct_value', 'ct_percentage', 'gross_profit', 'kickback_amount', 'commission_agent_2', 'agent_commission']
    f = open('accounts_headers.json')
    columns = json.load(f)
    col = columns["big_headers"]
    return jsonify(data=deals, columns = col, sum_keys=sum_keys)

def safe_float(value):
    if value == 'None' or value == '':
        return 0.0
    return float(str(value).replace(',', ''))
