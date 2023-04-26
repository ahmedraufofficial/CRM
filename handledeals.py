from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.elements import Null
from sqlalchemy.util.langhelpers import NoneType
from models import Deals, Leads, Properties, User
from forms import AddDealForm
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
from datetime import datetime, timedelta
from functions import *
from sqlalchemy import or_, and_

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'static/uploads')
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)




db = SQLAlchemy()

handledeals = Blueprint('handledeals', __name__, template_folder='templates')

@handledeals.route('/update_listing/<ref>/<con>/<con_name>/<con_number>/<con_email>/<transaction_type>',methods = ['GET','POST'])
@login_required
def update_listing(ref,con,con_name,con_number,con_email,transaction_type):
    if ref != None:    
        property = db.session.query(Properties).filter_by(refno=ref).first()
        if transaction_type == "Leased":
            property.tenant = con+" | "+con_name+" | "+str(con_number)
        else:
            property.owner = con
            property.owner_name = con_name
            property.owner_contact = con_number
            property.owner_email = con_email
        db.session.commit()
    return redirect(url_for('handledeals.display_deals'))

def update_lead(lead_ref,status,sub_status,user):
    if lead_ref != "":
        a = db.session.query(Leads).filter_by(refno = lead_ref).first()
        a.sub_status = "Successful"
        a.status = "Closed"
        db.session.commit()
        update_lead_note(user,lead_ref,"In lead pool",status,sub_status)
        update_user_note(user,lead_ref,status,sub_status)


@handledeals.route('/deals',methods = ['GET','POST'])
@login_required
def display_deals():   
    if current_user.deal == False:
        return abort(404)
    data = []
    if current_user.is_admin == True or current_user.job_title == "Manager" or current_user.job_title == "Accountant":
        for r in db.session.query(Deals).all():
            listing_sale = db.session.query(Properties).filter(and_(Properties.refno == r.listing_ref,Properties.owner == r.contact_buyer,r.type == "Sale")).first()
            listing_rent = db.session.query(Properties).filter(and_(Properties.refno == r.listing_ref,r.type == "Rent")).first()
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            #if r.listing_ref == "" or r.listing_ref == None:
            #    transfer = '<label class="btn btn-danger si" style="width:100% !important;">Missing Listing Info</label>'
            #else:
            #    transfer = '<a href="/update_listing/'+r.listing_ref+'/'+r.contact_buyer+'/'+r.contact_buyer_name+'/'+r.contact_buyer_number+'/'+r.contact_buyer_email+'/'+r.transaction_type+'"><button class="btn btn-warning si" style="width:100% !important;">Update Transfer/Tenant</button></a>'
            if listing_rent:
                if listing_rent.tenant:
                    a = listing_rent.tenant.split(" | ")[0]
                    if a == r.contact_buyer:
                        transfer = '<label class="btn si3" style="width:70% !important; background-color: green !important; padding: 2% !important; margin-right: 3px !important;">Deal Successful</label>'
                    else:
                        transfer = '<label class="btn si3" style="width:70% !important; background-color: #293645 !important; padding: 2% !important; padding: 7% !important; margin-right: 3px !important;">Pending Approval</label>'
                else:
                    transfer = '<label class="btn si3" style="width:70% !important; background-color: #293645 !important; padding: 2% !important; padding: 7% !important; margin-right: 3px !important;">Pending Approval</label>'
            elif listing_sale:
                transfer = '<label class="btn si3" style="width:70% !important; background-color: green !important; padding: 7% !important; margin-right: 3px !important;">Deal Successful</label>'
            else:
                transfer = '<label class="btn si3" style="width:70% !important; background-color: #293645 !important; padding: 7% !important; margin-right: 3px !important;">Pending Approval</label>'

            if current_user.is_admin == True:
                delete_btn = '<button class="btn-secondary si2" style="color:white;" data-toggle="modal" data-target="#deleteModal01" onclick="delete_('+"'"+new['refno']+"'"+')"><i class="bi bi-trash"></i></button>'
            else:
                delete_btn = ''
            
            if new['agent_pending'] == '0':
                comm_status = '<label class="btn si3" style="width:100% !important; background-color: green !important; padding: 7% !important">Commission Completed</label>'
            else:
                comm_status = '<label class="btn si3" style="width:100% !important; background-color: #293645 !important; padding: 7% !important">Commission Pending</label>'

            for k in ['transaction_type','source','priority','deposit','agency_fee_seller','agency_fee_buyer','gross_commission','include_vat','total_commission','split_with_external_referral','commission_agent_1','agent_2','commission_agent_2','estimated_deal_date','actual_deal_date','unit_no','unit_category','unit_beds','unit_floor','unit_type','buyer_type','finance_type','tenancy_start_date','tenancy_renewal_date','cheques']: new.pop(k)
            edit_btn = '<a href="/edit_deal/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
            new["edit"] = "<div style='display:flex;'>"+edit_btn+delete_btn+transfer+"</div>"
            new["edit01"] = "<div style='display:flex;'>"+comm_status+"</div>"
            data.append(new)

    elif current_user.sale == True or current_user.listing == True:
        for r in db.session.query(Deals).filter(or_(Deals.agent_1 == current_user.username,Deals.agent_2 == current_user.username)):
            listing_sale = db.session.query(Properties).filter(and_(Properties.refno == r.listing_ref,Properties.owner == r.contact_buyer,r.type == "Sale")).first()
            listing_rent = db.session.query(Properties).filter(and_(Properties.refno == r.listing_ref,r.type == "Rent")).first()
            row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
            new = row2dict(r)
            #if r.listing_ref == "" or r.listing_ref == None:
            #    transfer = '<label class="btn btn-danger si" style="width:100% !important;">Missing Listing Info</label>'
            #else:
            #    transfer = '<a href="/update_listing/'+r.listing_ref+'/'+r.contact_buyer+'/'+r.contact_buyer_name+'/'+r.contact_buyer_number+'/'+r.contact_buyer_email+'/'+r.transaction_type+'"><button class="btn btn-warning si" style="width:100% !important;">Update Transfer/Tenant</button></a>'
            if listing_rent:
                if listing_rent.tenant:
                    a = listing_rent.tenant.split(" | ")[0]
                    if a == r.contact_buyer:
                        transfer = '<label class="btn si3" style="width:70% !important; background-color: green !important; padding: 2% !important; margin-right: 3px !important;">Deal Successful</label>'
                    else:
                        transfer = '<label class="btn si3" style="width:70% !important; background-color: #293645 !important; padding: 2% !important; padding: 7% !important; margin-right: 3px !important;">Pending Approval</label>'
                else:
                    transfer = '<label class="btn si3" style="width:70% !important; background-color: #293645 !important; padding: 2% !important; padding: 7% !important; margin-right: 3px !important;">Pending Approval</label>'
            elif listing_sale:
                transfer = '<label class="btn si3" style="width:100% !important; background-color: green !important; padding: 7% !important; margin-right: 3px !important;">Deal Successful</label>'
            else:
                transfer = '<label class="btn si3" style="width:70% !important; background-color: #293645 !important; padding: 2% !important; padding: 7% !important; margin-right: 3px !important;">Pending Approval</label>'

            for k in ['transaction_type','source','priority','deposit','agency_fee_seller','agency_fee_buyer','gross_commission','include_vat','total_commission','split_with_external_referral','commission_agent_1','agent_2','commission_agent_2','estimated_deal_date','actual_deal_date','unit_no','unit_category','unit_beds','unit_floor','unit_type','buyer_type','finance_type','tenancy_start_date','tenancy_renewal_date','cheques']: new.pop(k)
            if current_user.sale == True:
                new['contact_seller_name'] = '-'
            else:
                pass
            if current_user.sale != True:
                new['agent_pending'] = '-'
                new['amount_eligible'] = '-'
            else:
                pass
            if new['agent_pending'] == '0':
                comm_status = '<label class="btn si3" style="width:100% !important; background-color: green !important; padding: 7% !important">Commission Completed</label>'
            else:
                comm_status = '<label class="btn si3" style="width:100% !important; background-color: #293645 !important; padding: 7% !important">Commission Pending</label>'
            if new['sm_approval'] == "Pending" and new['lm_approval'] == "Pending":
                    edit_btn = '<a href="/edit_deal/'+str(new['refno'])+'"><button  class="btn-primary si2"><i class="bi bi-pen"></i></button></a>'
            else:
                    edit_btn = ""
            new["edit"] = "<div style='display:flex;'>"+edit_btn+transfer+"</div>"
            new["edit01"] = "<div style='display:flex;'>"+comm_status+"</div>"
            data.append(new)

    f = open('deal_headers.json')
    columns = json.load(f)
    columns = columns["headers"]
    all_users = db.session.query(User).filter(or_(User.listing == True, User.sale == True)).all()
    return render_template('deals.html', data = data , columns = columns, user = current_user.username, all_users = all_users)

    
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
        source = form.source.data
        status = form.status.data
        sub_status = form.sub_status.data
        priority = form.priority.data
        deal_price = form.deal_price.data
        #deposit = form.deposit.data
        #agency_fee_seller = form.agency_fee_seller.data
        #agency_fee_buyer = form.agency_fee_buyer.data
        gross_commission = form.gross_commission.data
        include_vat = form.include_vat.data
        total_commission = form.total_commission.data
        #split_with_external_referral = form.split_with_external_referral.data
        cheques = form.cheques.data
        #estimated_deal_date = form.estimated_deal_date.data
        actual_deal_date = form.actual_deal_date.data
        unit_no = form.unit_no.data
        unit_category = form.unit_category.data
        unit_beds = form.unit_beds.data
        #unit_location = form.unit_location.data
        w = open('abudhabi.json')
        file_data = json.load(w)
        try:
            unit_location = file_data[form.unit_location.data]
        except:
            unit_location = "None"
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
        #sale
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        agent_2 = form.agent_2.data

        if form.sm_approval.data != None:
            sm_approval = form.sm_approval.data
        else:
            sm_approval = 'Pending'
        if form.lm_approval.data != None:
            lm_approval = form.lm_approval.data
        else:
            lm_approval = 'Pending'
        if form.admin_approval.data != None:
            admin_approval = form.admin_approval.data
        else:
            admin_approval = 'Pending'

        created_date = datetime.now()+timedelta(hours=4)
        updated_date = datetime.now()+timedelta(hours=4)

        if current_user.sale == True and current_user.listing == False:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,cheques=cheques,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,tenancy_start_date=tenancy_start_date,tenancy_renewal_date=tenancy_renewal_date,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,number_cheque_payment = number_cheque_payment,cheque_payment_type=cheque_payment_type,move_in_date = move_in_date, referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)    
        #listing
        elif current_user.listing == True and current_user.sale == False:
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,listing_ref=listing_ref,contact_seller=contact_seller,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,cheques=cheques,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_2=agent_2,commission_agent_2=commission_agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,tenancy_start_date=tenancy_start_date,tenancy_renewal_date=tenancy_renewal_date,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,number_cheque_payment = number_cheque_payment,cheque_payment_type=cheque_payment_type,move_in_date = move_in_date, referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)
        else:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,listing_ref=listing_ref,contact_seller=contact_seller,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,cheques=cheques,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,tenancy_start_date=tenancy_start_date,tenancy_renewal_date=tenancy_renewal_date,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,number_cheque_payment = number_cheque_payment,cheque_payment_type=cheque_payment_type,move_in_date = move_in_date, referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)

        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)

        try:
            passport01 = secure_filename(form.passport.data.filename)
            emi = secure_filename(form.emi_id.data.filename)
            directory = UPLOAD_FOLDER+'/'+newdeal.refno
            if not os.path.isdir(directory):
                os.mkdir(directory)
            form.passport.data.save(os.path.join(directory, passport01))
            newdeal.passport = ('/static/uploads'+'/UNI-D-'+str(newdeal.id)+"/"+passport01)
            form.emi_id.data.save(os.path.join(directory, emi))
            newdeal.eid = ('/static/uploads'+'/UNI-D-'+str(newdeal.id)+"/"+emi)
        except:
            newdeal.passport = ""
            newdeal.eid = ""

        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        #update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email,transaction_type)
        #update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "rent" , loc = "", radio_enable="disabled", old_eid = "", old_passport = "")

    
@handledeals.route('/add_deal/sale', methods = ['GET','POST'])
@login_required
def add_deal_sale(): 
    if current_user.deal == False:
        return abort(404)
    form = AddDealForm()
    w = open('abudhabi.json')
    mydict = json.load(w)
    newie = form.unit_location.data
    if request.method == 'POST': 
        type = "Sale"
        deal_type = "Primary"
        transaction_type = form.transaction_type.data
        created_by = current_user.username
        listing_ref = form.listing_ref.data
        source = form.source.data
        status = form.status.data
        sub_status = form.sub_status.data
        priority = form.priority.data
        deal_price = form.deal_price.data
        #deposit = form.deposit.data
        #agency_fee_seller = form.agency_fee_seller.data
        #agency_fee_buyer = form.agency_fee_buyer.data
        gross_commission = form.gross_commission.data
        include_vat = form.include_vat.data
        total_commission = form.total_commission.data
        #split_with_external_referral = form.split_with_external_referral.data
        #estimated_deal_date = form.estimated_deal_date.data
        actual_deal_date = form.actual_deal_date.data
        unit_no = form.unit_no.data
        unit_category = form.unit_category.data
        unit_beds = form.unit_beds.data
        try:
            unit_location = mydict[newie]
        except:
            unit_location = ""
        unit_sub_location = form.unit_sub_location.data
        unit_floor = form.unit_floor.data
        unit_type = form.unit_type.data
        #buyer_type = form.buyer_type.data
        finance_type = form.finance_type.data
        down_payment_available = form.down_payment_available.data
        down_payment = form.down_payment.data
        client_referred_bank = form.client_referred_bank.data
        bank_representative_name = form.bank_representative_name.data
        bank_representative_mobile = form.bank_representative_mobile.data
        referral_date = form.referral_date.data
        #sale
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        agent_2 = form.agent_2.data

        if form.sm_approval.data != None:
            sm_approval = form.sm_approval.data
        else:
            sm_approval = 'Pending'
        if form.lm_approval.data != None:
            lm_approval = form.lm_approval.data
        else:
            lm_approval = 'Pending'
        if form.admin_approval.data != None:
            admin_approval = form.admin_approval.data
        else:
            admin_approval = 'Pending'

        created_date = datetime.now()+timedelta(hours=4)
        updated_date = datetime.now()+timedelta(hours=4)



        if current_user.sale == True and current_user.listing == False:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)    
        #listing
        elif current_user.listing == True and current_user.sale == False:
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_2=agent_2,commission_agent_2=commission_agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)
        else:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)

        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)

        try:
            passport01 = secure_filename(form.passport.data.filename)
            emi = secure_filename(form.emi_id.data.filename)
            directory = UPLOAD_FOLDER+'/'+newdeal.refno
            if not os.path.isdir(directory):
                os.mkdir(directory)
            form.passport.data.save(os.path.join(directory, passport01))
            newdeal.passport = ('/static/uploads'+'/UNI-D-'+str(newdeal.id)+"/"+passport01)
            form.emi_id.data.save(os.path.join(directory, emi))
            newdeal.eid = ('/static/uploads'+'/UNI-D-'+str(newdeal.id)+"/"+emi)
        except:
            newdeal.passport = ""
            newdeal.eid = ""

        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        #update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email,transaction_type)
        #update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "sale",loc = "", radio_enable="disabled", old_eid = "", old_passport = "")

    
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

        #sale
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        agent_2 = form.agent_2.data
        
        
        

        if current_user.sale == True and current_user.listing == False:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,buyer_type=buyer_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,plot_size = plot_size,floor_no = floor_no,project = project,unit_price = unit_price,percentage = percentage,amount = amount,pre_approval_loan = pre_approval_loan,loan_amount = loan_amount,referral_date = referral_date)    
        #listing
        elif current_user.listing == True and current_user.sale == False:
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_2=agent_2,commission_agent_2=commission_agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,buyer_type=buyer_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,plot_size = plot_size,floor_no = floor_no,project = project,unit_price = unit_price,percentage = percentage,amount = amount,pre_approval_loan = pre_approval_loan,loan_amount = loan_amount,referral_date = referral_date)
        else:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,buyer_type=buyer_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,plot_size = plot_size,floor_no = floor_no,project = project,unit_price = unit_price,percentage = percentage,amount = amount,pre_approval_loan = pre_approval_loan,loan_amount = loan_amount,referral_date = referral_date)

        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)

        try:
            passport01 = secure_filename(form.passport.data.filename)
            emi = secure_filename(form.emi_id.data.filename)
            directory = UPLOAD_FOLDER+'/'+newdeal.refno
            dev = secure_filename(form.dev.data.filename)
            if not os.path.isdir(directory):
                os.mkdir(directory)
            form.passport.data.save(os.path.join(directory, passport01))
            newdeal.passport = ('/static/uploads'+'/UNI-S-'+str(newdeal.id)+"/"+passport01)
            form.emi_id.data.save(os.path.join(directory, emi))
            newdeal.eid = ('/static/uploads'+'/UNI-S-'+str(newdeal.id)+"/"+emi)
            form.developer_doc.data.save(os.path.join(directory, dev))
        except:
            newdeal.passport = ""
            newdeal.eid = ""
        
        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        #update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email,transaction_type)
        #update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "sale",loc = "", type="developer" , radio_enable="disabled")



@handledeals.route('/add_deal/rent/<variable>', methods = ['GET','POST'])
@login_required
def add_closed_deal_rent(variable): 
    if current_user.deal == False:
        return abort(404)
    lead = db.session.query(Leads).filter_by(refno=variable).first()
    form = AddDealForm()
    form.lead_ref.data = variable
    form.contact_buyer.data = lead.contact
    form.contact_buyer_name.data = lead.contact_name
    form.contact_buyer_number.data = lead.contact_number
    form.contact_buyer_email.data = lead.contact_email
    form.source.data = lead.source
    if request.method == 'POST': 
        type = "Rent"
        deal_type = "Primary"
        transaction_type = form.transaction_type.data
        created_by = current_user.username
        listing_ref = form.listing_ref.data
        source = form.source.data
        status = form.status.data
        sub_status = form.sub_status.data
        priority = form.priority.data
        deal_price = form.deal_price.data
        #deposit = form.deposit.data
        #agency_fee_seller = form.agency_fee_seller.data
        #agency_fee_buyer = form.agency_fee_buyer.data
        gross_commission = form.gross_commission.data
        include_vat = form.include_vat.data
        total_commission = form.total_commission.data
        #split_with_external_referral = form.split_with_external_referral.data
        cheques = form.cheques.data
        #estimated_deal_date = form.estimated_deal_date.data
        actual_deal_date = form.actual_deal_date.data
        unit_no = form.unit_no.data
        unit_category = form.unit_category.data
        unit_beds = form.unit_beds.data
        #unit_location = form.unit_location.data
        w = open('abudhabi.json')
        file_data = json.load(w)
        try:
            unit_location = file_data[form.unit_location.data]
        except:
            unit_location = "None"
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
        #sale
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        agent_2 = form.agent_2.data

        if form.sm_approval.data != None:
            sm_approval = form.sm_approval.data
        else:
            sm_approval = 'Pending'
        if form.lm_approval.data != None:
            lm_approval = form.lm_approval.data
        else:
            lm_approval = 'Pending'
        if form.admin_approval.data != None:
            admin_approval = form.admin_approval.data
        else:
            admin_approval = 'Pending'

        created_date = datetime.now()+timedelta(hours=4)
        updated_date = datetime.now()+timedelta(hours=4)

        if current_user.sale == True and current_user.listing == False:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,cheques=cheques,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,tenancy_start_date=tenancy_start_date,tenancy_renewal_date=tenancy_renewal_date,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,number_cheque_payment = number_cheque_payment,cheque_payment_type=cheque_payment_type,move_in_date = move_in_date, referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)    
        #listing
        elif current_user.listing == True and current_user.sale == False:
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,listing_ref=listing_ref,contact_seller=contact_seller,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,cheques=cheques,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_2=agent_2,commission_agent_2=commission_agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,tenancy_start_date=tenancy_start_date,tenancy_renewal_date=tenancy_renewal_date,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,number_cheque_payment = number_cheque_payment,cheque_payment_type=cheque_payment_type,move_in_date = move_in_date, referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)
        else:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,listing_ref=listing_ref,contact_seller=contact_seller,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,cheques=cheques,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,tenancy_start_date=tenancy_start_date,tenancy_renewal_date=tenancy_renewal_date,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,number_cheque_payment = number_cheque_payment,cheque_payment_type=cheque_payment_type,move_in_date = move_in_date, referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)

        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)

        try:
            passport01 = secure_filename(form.passport.data.filename)
            emi = secure_filename(form.emi_id.data.filename)
            directory = UPLOAD_FOLDER+'/'+newdeal.refno
            if not os.path.isdir(directory):
                os.mkdir(directory)
            form.passport.data.save(os.path.join(directory, passport01))
            newdeal.passport = ('/static/uploads'+'/UNI-D-'+str(newdeal.id)+"/"+passport01)
            form.emi_id.data.save(os.path.join(directory, emi))
            newdeal.eid = ('/static/uploads'+'/UNI-D-'+str(newdeal.id)+"/"+emi)
        except:
            newdeal.passport = ""
            newdeal.eid = ""

        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        #update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email,transaction_type)
        #update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "rent", building = "", loc = "" , radio_enable="disabled", old_eid = "", old_passport = "")

    
@handledeals.route('/add_deal/sale/<variable>', methods = ['GET','POST'])
@login_required
def add_closed_deal_sale(variable): 
    if current_user.deal == False:
        return abort(404)
    lead = db.session.query(Leads).filter_by(refno=variable).first()
    form = AddDealForm()
    form.lead_ref.data = variable
    form.contact_buyer.data = lead.contact
    form.contact_buyer_name.data = lead.contact_name
    form.contact_buyer_number.data = lead.contact_number
    form.contact_buyer_email.data = lead.contact_email
    form.source.data = lead.source
    w = open('abudhabi.json')
    mydict = json.load(w)
    newie = form.unit_location.data
    if request.method == 'POST': 
        type = "Sale"
        deal_type = "Primary"
        transaction_type = form.transaction_type.data
        created_by = current_user.username
        listing_ref = form.listing_ref.data
        source = form.source.data
        status = form.status.data
        sub_status = form.sub_status.data
        priority = form.priority.data
        deal_price = form.deal_price.data
        #deposit = form.deposit.data
        #agency_fee_seller = form.agency_fee_seller.data
        #agency_fee_buyer = form.agency_fee_buyer.data
        gross_commission = form.gross_commission.data
        include_vat = form.include_vat.data
        total_commission = form.total_commission.data
        #split_with_external_referral = form.split_with_external_referral.data
        #estimated_deal_date = form.estimated_deal_date.data
        actual_deal_date = form.actual_deal_date.data
        unit_no = form.unit_no.data
        unit_category = form.unit_category.data
        unit_beds = form.unit_beds.data
        try:
            unit_location = mydict[newie]
        except:
            unit_location = ""
        unit_sub_location = form.unit_sub_location.data
        unit_floor = form.unit_floor.data
        unit_type = form.unit_type.data
        #buyer_type = form.buyer_type.data
        finance_type = form.finance_type.data
        down_payment_available = form.down_payment_available.data
        down_payment = form.down_payment.data
        client_referred_bank = form.client_referred_bank.data
        bank_representative_name = form.bank_representative_name.data
        bank_representative_mobile = form.bank_representative_mobile.data
        referral_date = form.referral_date.data
        #sale
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        agent_2 = form.agent_2.data

        if form.sm_approval.data != None:
            sm_approval = form.sm_approval.data
        else:
            sm_approval = 'Pending'
        if form.lm_approval.data != None:
            lm_approval = form.lm_approval.data
        else:
            lm_approval = 'Pending'
        if form.admin_approval.data != None:
            admin_approval = form.admin_approval.data
        else:
            admin_approval = 'Pending'

        created_date = datetime.now()+timedelta(hours=4)
        updated_date = datetime.now()+timedelta(hours=4)



        if current_user.sale == True and current_user.listing == False:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)    
        #listing
        elif current_user.listing == True and current_user.sale == False:
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_2=agent_2,commission_agent_2=commission_agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)
        else:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,referral_date=referral_date, created_date = created_date, updated_date = updated_date, sm_approval = sm_approval, lm_approval = lm_approval, admin_approval=admin_approval)

        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)

        try:
            passport01 = secure_filename(form.passport.data.filename)
            emi = secure_filename(form.emi_id.data.filename)
            directory = UPLOAD_FOLDER+'/'+newdeal.refno
            if not os.path.isdir(directory):
                os.mkdir(directory)
            form.passport.data.save(os.path.join(directory, passport01))
            newdeal.passport = ('/static/uploads'+'/UNI-D-'+str(newdeal.id)+"/"+passport01)
            form.emi_id.data.save(os.path.join(directory, emi))
            newdeal.eid = ('/static/uploads'+'/UNI-D-'+str(newdeal.id)+"/"+emi)
        except:
            newdeal.passport = ""
            newdeal.eid = ""

        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "sale", radio_enable="disabled", old_eid = "", old_passport = "" )


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

        #sale
        lead_ref = form.lead_ref.data
        contact_buyer = form.contact_buyer.data
        contact_buyer_name = form.contact_buyer_name.data
        contact_buyer_number = form.contact_buyer_number.data
        contact_buyer_email = form.contact_buyer_email.data
        agent_2 = form.agent_2.data
        try:
            passport = secure_filename(form.passport.data.filename)
            emi = secure_filename(form.emi_id.data.filename)
            dev = secure_filename(form.dev.data.filename)
        except:
            return "Upload the necessary documents!"
        directory = UPLOAD_FOLDER+'/'+contact_buyer
        if not os.path.isdir(directory):
            os.mkdir(directory)
        form.passport.data.save(os.path.join(directory, passport))
        form.emi_id.data.save(os.path.join(directory, emi))
        form.developer_doc.data.save(os.path.join(directory, dev))

        if current_user.sale == True and current_user.listing == False:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,buyer_type=buyer_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,plot_size = plot_size,floor_no = floor_no,project = project,unit_price = unit_price,percentage = percentage,amount = amount,pre_approval_loan = pre_approval_loan,loan_amount = loan_amount,referral_date = referral_date)    
        #listing
        elif current_user.listing == True and current_user.sale == False:
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_2=agent_2,commission_agent_2=commission_agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,buyer_type=buyer_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,plot_size = plot_size,floor_no = floor_no,project = project,unit_price = unit_price,percentage = percentage,amount = amount,pre_approval_loan = pre_approval_loan,loan_amount = loan_amount,referral_date = referral_date)
        else:
            agent_1 = form.agent_1.data
            commission_agent_1 = form.commission_agent_1.data
            contact_seller = form.contact_seller.data
            contact_seller_name = form.contact_seller_name.data
            contact_seller_number = form.contact_seller_number.data
            contact_seller_email = form.contact_seller_email.data
            commission_agent_2 = form.commission_agent_2.data
            newdeal = Deals(type=type,deal_type=deal_type,transaction_type=transaction_type,created_by=created_by,listing_ref=listing_ref,lead_ref=lead_ref,contact_buyer=contact_buyer,contact_seller=contact_seller,contact_buyer_name=contact_buyer_name,contact_buyer_number=contact_buyer_number,contact_buyer_email=contact_buyer_email,contact_seller_name=contact_seller_name,contact_seller_number=contact_seller_number,contact_seller_email=contact_seller_email,source=source,status=status,sub_status=sub_status,priority=priority,deal_price=deal_price,deposit=deposit,agency_fee_seller=agency_fee_seller,agency_fee_buyer=agency_fee_buyer,gross_commission=gross_commission,include_vat=include_vat,total_commission=total_commission,split_with_external_referral=split_with_external_referral,agent_1=agent_1,commission_agent_1=commission_agent_1,agent_2=agent_2,commission_agent_2=commission_agent_2,estimated_deal_date=estimated_deal_date,actual_deal_date=actual_deal_date,unit_no=unit_no,unit_category=unit_category,unit_beds=unit_beds,unit_location=unit_location,unit_sub_location=unit_sub_location,unit_floor=unit_floor,unit_type=unit_type,buyer_type=buyer_type,finance_type=finance_type,down_payment_available = down_payment_available,down_payment = down_payment,client_referred_bank = client_referred_bank,bank_representative_name = bank_representative_name,bank_representative_mobile = bank_representative_mobile,plot_size = plot_size,floor_no = floor_no,project = project,unit_price = unit_price,percentage = percentage,amount = amount,pre_approval_loan = pre_approval_loan,loan_amount = loan_amount,referral_date = referral_date)


        
        db.session.add(newdeal)
        db.session.commit()
        db.session.refresh(newdeal)
        newdeal.refno = 'UNI-D-'+str(newdeal.id)
        db.session.commit()
        logs(current_user.username,'UNI-D-'+str(newdeal.id),'Added Deal')
        #update_listing(newdeal.listing_ref, contact_buyer,contact_buyer_name,contact_buyer_number,contact_buyer_email,transaction_type)
        update_lead(lead_ref,status,sub_status,current_user.username)
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form, user = current_user.username, purpose = "sale", building = building, loc = loc, radio_enable="disabled" )




@handledeals.route('/edit_deal/<variable>', methods = ['GET','POST'])
@login_required
def edit_deal(variable):
    if current_user.deal == False or current_user.edit == False:
        return abort(404) 
    edit = db.session.query(Deals).filter_by(refno=variable).first()
    form = AddDealForm(obj = edit)
    w = open('abudhabi.json')
    mydict = json.load(w)
    new = form.unit_location.data
    try:
        form.unit_location.data = list(mydict.keys())[list(mydict.values()).index(edit.unit_location)]
    except:
        form.unit_location.data = ""
    old_eid = edit.eid
    old_passport = edit.passport
    purpose = edit.type.lower()
    print(purpose)
    if request.method == 'POST':
        form.populate_obj(edit)
        edit.updated_date = datetime.now()+timedelta(hours=4)
        try:
            edit.unit_location = mydict[new]
        except:
            edit.unit_location = ""
        try:
            file_filename = secure_filename(form.emi_id.data.filename)
            directory = UPLOAD_FOLDER+'/'+edit.refno
            if not os.path.isdir(directory):
                os.mkdir(directory)
            form.passport.data.save(os.path.join(directory, file_filename))
            form.emi_id.data.save(os.path.join(directory, file_filename))
            form.developer_doc.data.save(os.path.join(directory, file_filename))
        except:
            pass
        if edit.sm_approval == "Approve" and edit.lm_approval == "Approve" and edit.admin_approval == "Approve":
            print("Lesssgooo")
            update_listing(edit.listing_ref, edit.contact_buyer, edit.contact_buyer_name, edit.contact_buyer_number, edit.contact_buyer_email, edit.transaction_type)
            update_lead(edit.lead_ref,edit.status,edit.sub_status,current_user.username) 
        else:
            pass
        db.session.commit()
        logs(current_user.username,'deal no','Edited Deal')
        return redirect(url_for('handledeals.display_deals'))
    return render_template('add_deal.html', form=form,assign=edit.agent_1,assign2=edit.agent_2, user = current_user.username,building = edit.unit_sub_location, radio_enable="enabled", old_eid = old_eid, old_passport = old_passport, purpose = purpose)

@handledeals.route('/delete_deal/<variable>', methods = ['GET','POST'])
@login_required
def delete_exitform(variable):
    delete = db.session.query(Deals).filter_by(refno=variable).first()
    db.session.delete(delete)
    db.session.commit()
    return redirect(url_for('handledeals.display_deals'))