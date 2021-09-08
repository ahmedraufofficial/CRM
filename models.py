from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()

class Contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    title = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    number = db.Column(db.Integer, unique=True)
    alternate_number = db.Column(db.Integer)
    contact_type = db.Column(db.String(50))
    role = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    source = db.Column(db.String(50))
    assign_to = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    email = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    date_of_birth = db.Column(db.DateTime)
    religion = db.Column(db.String(50))
    language = db.Column(db.String(50))
    comment = db.Column(db.String(150))

class Properties(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    city = db.Column(db.Integer)
    type = db.Column(db.String(50))
    subtype = db.Column(db.String(50))
    created_by = db.Column(db.String(50))
    commercialtype = db.Column(db.String(50))
    refno = db.Column(db.String(50))
    title = db.Column(db.String(200))
    description = db.Column(db.String(10000))
    unit = db.Column(db.String(50))
    plot = db.Column(db.String(50))
    street = db.Column(db.String(50))
    size = db.Column(db.Float)
    plot_size = db.Column(db.Float)
    price = db.Column(db.Integer)
    rentpriceterm = db.Column(db.String(50))
    price_per_area = db.Column(db.Float)
    commission = db.Column(db.String(50))
    deposit = db.Column(db.String(50))
    bedrooms = db.Column(db.String(20))
    lastupdated = db.Column(db.DateTime)
    contactemail = db.Column(db.String(100))
    contactnumber = db.Column(db.Integer)
    locationtext = db.Column(db.String(50))
    furnished = db.Column(db.Integer)
    building = db.Column(db.String(80))
    privateamenities = db.Column(db.String(500))
    commercialamenities = db.Column(db.String(500))
    photos = db.Column(db.String(10000))
    geopoint = db.Column(db.String(50))
    bathrooms = db.Column(db.Integer)
    permit_number = db.Column(db.String(50))
    view360 = db.Column(db.String(50))
    video_url = db.Column(db.String(100))
    completion_status = db.Column(db.String(100))
    source = db.Column(db.String(100))
    owner = db.Column(db.String(50))
    owner_name = db.Column(db.String(80))
    owner_contact = db.Column(db.String(50))
    owner_email = db.Column(db.String(100))
    tenant = db.Column(db.String(50))
    expiry_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    assign_to = db.Column(db.String(50))
    tenure = db.Column(db.String(50))
    featured = db.Column(db.String(50))
    parking = db.Column(db.Integer)
    offplan_status = db.Column(db.String(100))
    portal = db.Column(db.String(100))


class Leads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    contact = db.Column(db.String(50))
    contact_name = db.Column(db.String(80))
    contact_number = db.Column(db.String(50))
    contact_email = db.Column(db.String(100))
    nationality = db.Column(db.String(100))
    role = db.Column(db.String(100))
    purpose = db.Column(db.String(50))
    time_to_contact = db.Column(db.DateTime)
    agent = db.Column(db.String(100))
    refno = db.Column(db.String(100))
    enquiry_date = db.Column(db.DateTime)
    lead_type = db.Column(db.String(50))
    finance_type = db.Column(db.String(50))
    privateamenities = db.Column(db.String(500))
    created_by = db.Column(db.String(50))
    status = db.Column(db.String(50))
    sub_status = db.Column(db.String(50))
    property_requirements = db.Column(db.String(50))
    locationtext = db.Column(db.String(50))
    building = db.Column(db.String(80))
    subtype = db.Column(db.String(50))
    min_beds = db.Column(db.String(50))
    max_beds = db.Column(db.String(50))
    min_price = db.Column(db.Integer)
    max_price = db.Column(db.Integer)
    finance_type = db.Column(db.String(50))
    unit = db.Column(db.String(50))
    plot = db.Column(db.String(50))
    street = db.Column(db.String(50))
    size = db.Column(db.Float)
    source = db.Column(db.String(50))

 
class Deals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    deal_type = db.Column(db.String(50))
    transaction_type = db.Column(db.String(50))
    refno = db.Column(db.String(100))
    created_by = db.Column(db.String(50))
    listing_ref = db.Column(db.String())
    lead_ref = db.Column(db.String(50))
    contact_buyer = db.Column(db.String(100))
    contact_buyer_name = db.Column(db.String(80))
    contact_buyer_number = db.Column(db.String(50))
    contact_buyer_email = db.Column(db.String(100))
    contact_seller = db.Column(db.String(100))
    contact_seller_name = db.Column(db.String(80))
    contact_seller_number = db.Column(db.String(50))
    contact_seller_email = db.Column(db.String(100))
    source = db.Column(db.String(50))
    status = db.Column(db.String(50))
    sub_status = db.Column(db.String(50))
    priority = db.Column(db.String(50))
    hot_lead = db.Column(db.String(50))
    deal_price = db.Column(db.Integer)
    deposit = db.Column(db.Integer)
    agency_fee_seller = db.Column(db.String(50))
    agency_fee_buyer = db.Column(db.String(50))
    gross_commission = db.Column(db.String(50))
    include_vat = db.Column(db.String(50))
    total_commission = db.Column(db.String(50))
    split_with_external_referral = db.Column(db.String(50))
    deal_type = db.Column(db.String(50))
    agent_1 = db.Column(db.String(50))
    commission_agent_1 = db.Column(db.String(50))
    agent_2 = db.Column(db.String(50))
    commission_agent_2 = db.Column(db.String(50))
    cheques = db.Column(db.String(50))
    estimated_deal_date = db.Column(db.String(50))
    actual_deal_date = db.Column(db.String(50))
    unit_no = db.Column(db.String(50))
    unit_category = db.Column(db.String(50))
    unit_beds = db.Column(db.String(50))
    unit_location = db.Column(db.String(100))
    unit_sub_location = db.Column(db.String(100))
    unit_floor = db.Column(db.String(50))
    unit_type = db.Column(db.String(50))
    buyer_type = db.Column(db.String(50))
    finance_type = db.Column(db.String(50))
    tenancy_start_date = db.Column(db.String(50))
    tenancy_renewal_date = db.Column(db.String(50))
    down_payment_available = db.Column(db.String(50))
    down_payment = db.Column(db.String(50))
    number_cheque_payment = db.Column(db.String(50))
    cheque_payment_type = db.Column(db.String(50))
    move_in_date = db.Column(db.DateTime)
    client_referred_bank = db.Column(db.String(50))
    bank_representative_name = db.Column(db.String(50))
    bank_representative_mobile = db.Column(db.String(50))
    referral_date = db.Column(db.DateTime)
    pre_approval_loan = db.Column(db.String(50))
    loan_amount = db.Column(db.String(50))
    project = db.Column(db.String(50))
    floor_no = db.Column(db.String(50))
    plot_size = db.Column(db.Float)
    unit_price = db.Column(db.String(50))
    percentage = db.Column(db.String(50))
    amount = db.Column(db.String(50))

