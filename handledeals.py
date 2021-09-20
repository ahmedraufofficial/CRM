from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models import Deals, Leads, Properties
from forms import AddDealForm
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import datetime
from functions import *


path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)




db = SQLAlchemy()

handledeals = Blueprint('handledeals', __name__, template_folder='templates')

def update_listing(ref,con,con_name,con_number,con_email):
    if ref != "":    
        property = db.session.query(Properties).filter_by(refno=ref).first()
        property.owner = con
        property.owner_name = con_name
        property.owner_contact = con_number
        property.owner_email = con_email
        db.session.commit()
        

def update_lead(lead_ref,status,sub_status,user):
    if lead_ref != "":
        a = db.session.query(Leads).filter_by(refno = lead_ref).first()
        a.sub_status = sub_status
        a.status = status
        db.session.commit()
        update_lead_note(user,lead_ref,"In lead pool",status,sub_status)
        update_user_note(user,lead_ref,status,sub_status)


@handledeals.route('/deals',methods = ['GET','POST'])
@login_required
def display_deals():   
    if current_user.deal == False:
        return abort(404)
    data = []
    for r in db.session.query(Deals).all():
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        new = row2dict(r)
        for k in ['transaction_type','created_by','listing_ref','lead_ref','source','priority','deposit','agency_fee_seller','agency_fee_buyer','gross_commission','include_vat','total_commission','split_with_external_referral','commission_agent_1','agent_2','commission_agent_2','estimated_deal_date','actual_deal_date','unit_no','unit_category','unit_beds','unit_location','unit_sub_location','unit_floor','unit_type','buyer_type','finance_type','tenancy_start_date','tenancy_renewal_date','cheques']: new.pop(k)
        new["edit"] = "<div style='display:flex;'>"+'<a href="/edit_deal/'+str(new['id'])+'"><button  class="btn btn-primary si">Edit</button></a>'+"</div>"
        data.append(new)
    f = open('deal_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    return render_template('deals.html', data = data , columns = columns, user = current_user.username)

    
@handledeals.route('/add_deal/rent', methods = ['GET','POST'])
@login_required
def add_deal_rent(): 
    if current_user.deal == False:
        return abort(404)
    form = AddDealForm()
    if request.method == 'POST': 
        type = "Rent"
        deal_type = "Primary"
        transaction_type = form.transaction_type.data
        created_by = current_user.username
        listing_ref = form.listing_ref.data
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        contact_seller = form.contact_seller.data
        contact_seller_name = form.contact_seller_name.data
        contact_seller_number = form.contact_seller_number.data
        contact_seller_email = form.contact_seller_email.data
        source = form.source.data
        status = form.status.data
        sub_status = form.sub_status.data
        priority = form.priority.data
        deal_price = form.deal_price.data
        deposit = form.deposit.data
        agency_fee_seller = form.agency_fee_seller.data
        agency_fee_buyer = form.agency_fee_buyer.data
        gross_commission = form.gross_commission.data
        include_vat = form.include_vat.data
        total_commission = form.total_commission.data
        split_with_external_referral = form.split_with_external_referral.data
        agent_1 = form.agent_1.data
        commission_agent_1 = form.commission_agent_1.data
        agent_2 = form.agent_2.data
        commission_agent_2 = form.commission_agent_2.data
        cheques = form.cheques.data
        estimated_deal_date = form.estimated_deal_date.data
        actual_deal_date = form.actual_deal_date.data
        unit_no = form.unit_no.data
        unit_category = form.unit_category.data
        unit_beds = form.unit_beds.data
        unit_location = form.unit_location.data
        unit_sub_location = form.unit_sub_location.data
        unit_floor = form.unit_floor.data
        unit_type = form.unit_type.data
        #buyer_type = form.buyer_type.data
        #finance_type = form.finance_type.data
        number_cheque_payment = form.number_cheque_payment.data
        cheque_payment_type = form.cheque_payment_type.data
        move_in_date = form.move_in_date.data
        tenancy_start_date = form.tenancy_start_date.data
        tenancy_renewal_date = form.tenancy_renewal_date.data
        client_referred_bank = form.client_referred_bank.data
        bank_representative_name = form.bank_representative_name.data
        bank_representative_mobile = form.bank_representative_mobile.data
        referral_date = form.referral_date.data
        file_filename = secure_filename(form.emi_id.data.filename)
        directory = UPLOAD_FOLDER+'/'+contact_buyer
        if not os.path.isdir(directory):
            os.mkdir(directory)
            form.emi_id.data.save(os.path.join(directory, file_filename))
        newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,cheques=cheques,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,tenancy_start_date=tenancy_start_date,tenancy_renewal_date=tenancy_renewal_date,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,number_cheque_payment = number_cheque_payment,cheque_payment_type=cheque_payment_type,move_in_date = move_in_date, referral_date=referral_date)
        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)
        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email)
        update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "rent" , loc = "")

    
@handledeals.route('/add_deal/sale', methods = ['GET','POST'])
@login_required
def add_deal_sale(): 
    if current_user.deal == False:
        return abort(404)
    form = AddDealForm()
    if request.method == 'POST': 
        type = "Sale"
        deal_type = "Primary"
        transaction_type = form.transaction_type.data
        created_by = current_user.username
        listing_ref = form.listing_ref.data
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        contact_seller = form.contact_seller.data
        contact_seller_name = form.contact_seller_name.data
        contact_seller_number = form.contact_seller_number.data
        contact_seller_email = form.contact_seller_email.data
        source = form.source.data
        status = form.status.data
        sub_status = form.sub_status.data
        priority = form.priority.data
        deal_price = form.deal_price.data
        deposit = form.deposit.data
        agency_fee_seller = form.agency_fee_seller.data
        agency_fee_buyer = form.agency_fee_buyer.data
        gross_commission = form.gross_commission.data
        include_vat = form.include_vat.data
        total_commission = form.total_commission.data
        split_with_external_referral = form.split_with_external_referral.data
        agent_1 = form.agent_1.data
        commission_agent_1 = form.commission_agent_1.data
        agent_2 = form.agent_2.data
        commission_agent_2 = form.commission_agent_2.data
        estimated_deal_date = form.estimated_deal_date.data
        actual_deal_date = form.actual_deal_date.data
        unit_no = form.unit_no.data
        unit_category = form.unit_category.data
        unit_beds = form.unit_beds.data
        unit_location = form.unit_location.data
        unit_sub_location = form.unit_sub_location.data
        unit_floor = form.unit_floor.data
        unit_type = form.unit_type.data
        buyer_type = form.buyer_type.data
        finance_type = form.finance_type.data
        down_payment_available = form.down_payment_available.data
        down_payment = form.down_payment.data
        client_referred_bank = form.client_referred_bank.data
        bank_representative_name = form.bank_representative_name.data
        bank_representative_mobile = form.bank_representative_mobile.data
        referral_date = form.referral_date.data
        file_filename = secure_filename(form.emi_id.data.filename)
        directory = UPLOAD_FOLDER+'/'+contact_buyer
        if not os.path.isdir(directory):
            os.mkdir(directory)
        form.emi_id.data.save(os.path.join(directory, file_filename))
        newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,buyer_type=buyer_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,referral_date=referral_date)
        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)
        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email)
        update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "sale",loc = "")

    
@handledeals.route('/add_deal/developer', methods = ['GET','POST'])
@login_required
def add_deal_developer(): 
    if current_user.deal == False:
        return abort(404)
    form = AddDealForm()
    if request.method == 'POST': 
        type = "Sale"
        deal_type = "Secondary"
        transaction_type = form.transaction_type.data
        created_by = current_user.username
        listing_ref = form.listing_ref.data
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        contact_seller = form.contact_seller.data
        contact_seller_name = form.contact_seller_name.data
        contact_seller_number = form.contact_seller_number.data
        contact_seller_email = form.contact_seller_email.data
        source = form.source.data
        status = form.status.data
        sub_status = form.sub_status.data
        priority = form.priority.data
        deal_price = form.deal_price.data
        deposit = form.deposit.data
        agency_fee_seller = form.agency_fee_seller.data
        agency_fee_buyer = form.agency_fee_buyer.data
        gross_commission = form.gross_commission.data
        include_vat = form.include_vat.data
        total_commission = form.total_commission.data
        split_with_external_referral = form.split_with_external_referral.data
        agent_1 = form.agent_1.data
        commission_agent_1 = form.commission_agent_1.data
        agent_2 = form.agent_2.data
        commission_agent_2 = form.commission_agent_2.data
        estimated_deal_date = form.estimated_deal_date.data
        actual_deal_date = form.actual_deal_date.data
        unit_no = form.unit_no.data
        unit_category = form.unit_category.data
        unit_beds = form.unit_beds.data
        unit_location = form.unit_location.data
        unit_sub_location = form.unit_sub_location.data
        unit_floor = form.unit_floor.data
        unit_type = form.unit_type.data
        buyer_type = form.buyer_type.data
        finance_type = form.finance_type.data
        down_payment_available = form.down_payment_available.data
        down_payment = form.down_payment.data
        client_referred_bank = form.client_referred_bank.data
        bank_representative_name = form.bank_representative_name.data
        bank_representative_mobile = form.bank_representative_mobile.data
        referral_date = form.referral_date.data
        plot_size = form.plot_size.data
        floor_no = form.floor_no.data
        project = form.project.data
        unit_price = form.unit_price.data
        percentage = form.percentage.data
        amount = form.amount.data
        pre_approval_loan = form.pre_approval_loan.data
        loan_amount = form.loan_amount.data
        file_filename = secure_filename(form.emi_id.data.filename)
        directory = UPLOAD_FOLDER+'/'+contact_buyer
        if not os.path.isdir(directory):
            os.mkdir(directory)
        form.emi_id.data.save(os.path.join(directory, file_filename))
        newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,buyer_type=buyer_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,plot_size = plot_size,floor_no = floor_no,project = project,unit_price = unit_price,percentage = percentage,amount = amount,pre_approval_loan = pre_approval_loan,loan_amount = loan_amount,referral_date = referral_date)
        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)
        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email)
        update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "sale",loc = "", type="developer")



@handledeals.route('/add_deal/rent/<variable>', methods = ['GET','POST'])
@login_required
def add_closed_deal_rent(variable): 
    if current_user.deal == False:
        return abort(404)
    lead = db.session.query(Leads).filter_by(refno=variable).first()
    print(lead)
    form = AddDealForm()
    form.lead_ref.data = variable
    loc = lead.locationtext
    building = lead.building
    form.unit_type.data = lead.subtype
    form.unit_beds.data = lead.min_beds
    form.deal_price.data = lead.min_price
    form.listing_ref.data = lead.property_requirements
    form.unit_no.data = lead.unit
    form.unit_floor.data = lead.plot
    if lead.property_requirements != "":
        property = db.session.query(Properties).filter_by(refno=lead.property_requirements).first()
        form.contact_seller.data = property.owner
        form.contact_seller_name.data = property.owner_name
        form.contact_seller_number.data = property.owner_contact
        form.contact_seller_email.data = property.owner_email
    form.contact_buyer.data = lead.contact
    form.contact_buyer_name.data = lead.contact_name
    form.contact_buyer_number.data = lead.contact_number
    form.contact_buyer_email.data = lead.contact_email
    if request.method == 'POST': 
        type = "Rent"
        deal_type = "Primary"
        transaction_type = form.transaction_type.data
        created_by = current_user.username
        listing_ref = form.listing_ref.data
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        contact_seller = form.contact_seller.data
        contact_seller_name = form.contact_seller_name.data
        contact_seller_number = form.contact_seller_number.data
        contact_seller_email = form.contact_seller_email.data
        source = form.source.data
        status = form.status.data
        sub_status = form.sub_status.data
        priority = form.priority.data
        deal_price = form.deal_price.data
        deposit = form.deposit.data
        agency_fee_seller = form.agency_fee_seller.data
        agency_fee_buyer = form.agency_fee_buyer.data
        gross_commission = form.gross_commission.data
        include_vat = form.include_vat.data
        total_commission = form.total_commission.data
        split_with_external_referral = form.split_with_external_referral.data
        agent_1 = form.agent_1.data
        commission_agent_1 = form.commission_agent_1.data
        agent_2 = form.agent_2.data
        commission_agent_2 = form.commission_agent_2.data
        cheques = form.cheques.data
        estimated_deal_date = form.estimated_deal_date.data
        actual_deal_date = form.actual_deal_date.data
        unit_no = form.unit_no.data
        unit_category = form.unit_category.data
        unit_beds = form.unit_beds.data
        unit_location = form.unit_location.data
        unit_sub_location = form.unit_sub_location.data
        unit_floor = form.unit_floor.data
        unit_type = form.unit_type.data
        #buyer_type = form.buyer_type.data
        #finance_type = form.finance_type.data
        number_cheque_payment = form.number_cheque_payment.data
        cheque_payment_type = form.cheque_payment_type.data
        move_in_date = form.move_in_date.data
        tenancy_start_date = form.tenancy_start_date.data
        tenancy_renewal_date = form.tenancy_renewal_date.data
        client_referred_bank = form.client_referred_bank.data
        bank_representative_name = form.bank_representative_name.data
        bank_representative_mobile = form.bank_representative_mobile.data
        referral_date = form.referral_date.data
        file_filename = secure_filename(form.emi_id.data.filename)
        directory = UPLOAD_FOLDER+'/'+contact_buyer
        if not os.path.isdir(directory):
            os.mkdir(directory)
        form.emi_id.data.save(os.path.join(directory, file_filename))
        newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,cheques=cheques,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,tenancy_start_date=tenancy_start_date,tenancy_renewal_date=tenancy_renewal_date,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,number_cheque_payment = number_cheque_payment,cheque_payment_type=cheque_payment_type,move_in_date = move_in_date, referral_date=referral_date)
        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)
        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email)
        update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "rent", building = building, loc = loc )

    
@handledeals.route('/add_deal/sale/<variable>', methods = ['GET','POST'])
@login_required
def add_closed_deal_sale(variable): 
    if current_user.deal == False:
        return abort(404)
    lead = db.session.query(Leads).filter_by(refno=variable).first()
    form = AddDealForm()
    form.lead_ref.data = variable
    loc = lead.locationtext
    building = lead.building
    form.unit_type.data = lead.subtype
    form.unit_beds.data = lead.min_beds
    form.deal_price.data = lead.min_price
    form.listing_ref.data = lead.property_requirements
    if lead.property_requirements != "":
        property = db.session.query(Properties).filter_by(refno=lead.property_requirements).first()
        form.contact_seller.data = property.owner
        form.contact_seller_name.data = property.owner_name
        form.contact_seller_number.data = property.owner_contact
        form.contact_seller_email.data = property.owner_email
    form.contact_buyer.data = lead.contact
    form.contact_buyer_name.data = lead.contact_name
    form.contact_buyer_number.data = lead.contact_number
    form.contact_buyer_email.data = lead.contact_email
    if request.method == 'POST': 
        type = "Sale"
        deal_type = "Primary"
        transaction_type = form.transaction_type.data
        created_by = current_user.username
        listing_ref = form.listing_ref.data
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        contact_seller = form.contact_seller.data
        contact_seller_name = form.contact_seller_name.data
        contact_seller_number = form.contact_seller_number.data
        contact_seller_email = form.contact_seller_email.data
        source = form.source.data
        status = form.status.data
        sub_status = form.sub_status.data
        priority = form.priority.data
        deal_price = form.deal_price.data
        deposit = form.deposit.data
        agency_fee_seller = form.agency_fee_seller.data
        agency_fee_buyer = form.agency_fee_buyer.data
        gross_commission = form.gross_commission.data
        include_vat = form.include_vat.data
        total_commission = form.total_commission.data
        split_with_external_referral = form.split_with_external_referral.data
        agent_1 = form.agent_1.data
        commission_agent_1 = form.commission_agent_1.data
        agent_2 = form.agent_2.data
        commission_agent_2 = form.commission_agent_2.data
        estimated_deal_date = form.estimated_deal_date.data
        actual_deal_date = form.actual_deal_date.data
        unit_no = form.unit_no.data
        unit_category = form.unit_category.data
        unit_beds = form.unit_beds.data
        unit_location = form.unit_location.data
        unit_sub_location = form.unit_sub_location.data
        unit_floor = form.unit_floor.data
        unit_type = form.unit_type.data
        buyer_type = form.buyer_type.data
        finance_type = form.finance_type.data
        down_payment_available = form.down_payment_available.data
        down_payment = form.down_payment.data
        client_referred_bank = form.client_referred_bank.data
        bank_representative_name = form.bank_representative_name.data
        bank_representative_mobile = form.bank_representative_mobile.data
        referral_date = form.referral_date.data
        file_filename = secure_filename(form.emi_id.data.filename)
        directory = UPLOAD_FOLDER+'/'+contact_buyer
        if not os.path.isdir(directory):
            os.mkdir(directory)
            form.emi_id.data.save(os.path.join(directory, file_filename))
        newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,buyer_type=buyer_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,referral_date=referral_date)
        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)
        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email)
        update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "sale", building = building, loc = loc )


@handledeals.route('/add_deal/developer/<variable>', methods = ['GET','POST'])
@login_required
def add_closed_deal_developer(variable): 
    if current_user.deal == False:
        return abort(404)
    lead = db.session.query(Leads).filter_by(refno=variable).first()
    form = AddDealForm()
    form.lead_ref.data = variable
    loc = lead.locationtext
    building = lead.building
    form.unit_type.data = lead.subtype
    form.unit_beds.data = lead.min_beds
    form.deal_price.data = lead.min_price
    form.listing_ref.data = lead.property_requirements
    if lead.property_requirements != "":
        property = db.session.query(Properties).filter_by(refno=lead.property_requirements).first()
        form.contact_seller.data = property.owner
        form.contact_seller_name.data = property.owner_name
        form.contact_seller_number.data = property.owner_contact
        form.contact_seller_email.data = property.owner_email
    form.contact_buyer.data = lead.contact
    form.contact_buyer_name.data = lead.contact_name
    form.contact_buyer_number.data = lead.contact_number
    form.contact_buyer_email.data = lead.contact_email
    if request.method == 'POST': 
        type = "Sale"
        deal_type = "Secondary"
        transaction_type = form.transaction_type.data
        created_by = current_user.username
        listing_ref = form.listing_ref.data
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        contact_seller = form.contact_seller.data
        contact_seller_name = form.contact_seller_name.data
        contact_seller_number = form.contact_seller_number.data
        contact_seller_email = form.contact_seller_email.data
        source = form.source.data
        status = form.status.data
        sub_status = form.sub_status.data
        priority = form.priority.data
        deal_price = form.deal_price.data
        deposit = form.deposit.data
        agency_fee_seller = form.agency_fee_seller.data
        agency_fee_buyer = form.agency_fee_buyer.data
        gross_commission = form.gross_commission.data
        include_vat = form.include_vat.data
        total_commission = form.total_commission.data
        split_with_external_referral = form.split_with_external_referral.data
        agent_1 = form.agent_1.data
        commission_agent_1 = form.commission_agent_1.data
        agent_2 = form.agent_2.data
        commission_agent_2 = form.commission_agent_2.data
        estimated_deal_date = form.estimated_deal_date.data
        actual_deal_date = form.actual_deal_date.data
        unit_no = form.unit_no.data
        unit_category = form.unit_category.data
        unit_beds = form.unit_beds.data
        unit_location = form.unit_location.data
        unit_sub_location = form.unit_sub_location.data
        unit_floor = form.unit_floor.data
        unit_type = form.unit_type.data
        buyer_type = form.buyer_type.data
        finance_type = form.finance_type.data
        down_payment_available = form.down_payment_available.data
        down_payment = form.down_payment.data
        client_referred_bank = form.client_referred_bank.data
        bank_representative_name = form.bank_representative_name.data
        bank_representative_mobile = form.bank_representative_mobile.data
        referral_date = form.referral_date.data
        plot_size = form.plot_size.data
        floor_no = form.floor_no.data
        project = form.project.data
        unit_price = form.unit_price.data
        percentage = form.percentage.data
        amount = form.amount.data
        pre_approval_loan = form.pre_approval_loan.data
        loan_amount = form.loan_amount.data
        file_filename = secure_filename(form.emi_id.data.filename)
        directory = UPLOAD_FOLDER+'/'+contact_buyer
        if not os.path.isdir(directory):
            os.mkdir(directory)
            form.emi_id.data.save(os.path.join(directory, file_filename))
        newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,buyer_type=buyer_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,plot_size = plot_size,floor_no = floor_no,project = project,unit_price = unit_price,percentage = percentage,amount = amount,pre_approval_loan = pre_approval_loan,loan_amount = loan_amount,referral_date = referral_date)
        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)
        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email)
        update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "sale", building = building, loc = loc )




@handledeals.route('/edit_deal/<variable>', methods = ['GET','POST'])
@login_required
def edit_deal(variable):
    if current_user.deal == False or current_user.edit == False:
        return abort(404) 
    edit = db.session.query(Deals).filter_by(id=variable).first()
    form = AddDealForm(obj = edit)
    if request.method == 'POST':
        form.populate_obj(edit)
        contact_buyer = form.contact_buyer.data
        try:
            file_filename = secure_filename(form.emi_id.data.filename)
            directory = UPLOAD_FOLDER+'/'+contact_buyer
            if not os.path.isdir(directory):
                os.mkdir(directory)
                form.emi_id.data.save(os.path.join(directory, file_filename))
        except:
            pass
        db.session.commit()
        logs(current_user.username,'deal no','Edited Deal')
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form,assign=edit.agent_1, user = current_user.username)

