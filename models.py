from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    email = db.Column(db.String(50))
    number = db.Column(db.Integer)
    job_title = db.Column(db.String(50))
    department = db.Column(db.String(50))
    profile_picture = db.Column(db.String())
    emp_code = db.Column(db.String(50))
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
    team_lead = db.Column(db.Boolean, default=False)
    abudhabi = db.Column(db.Boolean, default=False)
    dubai = db.Column(db.Boolean, default=False)
    qa = db.Column(db.Boolean, default=False)
    team_members = db.Column(db.String(200))

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
    created_at = db.Column(db.DateTime)
    view = db.Column(db.String(50))
    floorplan = db.Column(db.String(1000))
    masterplan = db.Column(db.String(1000))
    cheques = db.Column(db.Integer)
    property_finder = db.Column(db.String(500))

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
    created_date = db.Column(db.DateTime)
    lead_type = db.Column(db.String(50))
    finance_type = db.Column(db.String(50))
    propertyamenities = db.Column(db.String(800))
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
    lastupdated = db.Column(db.DateTime)
    city = db.Column(db.String(50))

 
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
    estimated_deal_date = db.Column(db.DateTime)
    actual_deal_date = db.Column(db.DateTime)
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
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    sm_approval = db.Column(db.String(50))
    lm_approval = db.Column(db.String(50))
    admin_approval = db.Column(db.String(50))
    passport = db.Column(db.String(500))
    eid = db.Column(db.String(500))
    amount_received = db.Column(db.String(50))
    agent_pers_comm = db.Column(db.String(50))
    amount_eligible = db.Column(db.String(50))
    agent_received = db.Column(db.String(50))
    agent_pending = db.Column(db.String(50))
    passport_seller = db.Column(db.String(500))
    eid_seller = db.Column(db.String(500))
    mou = db.Column(db.String(500))
    tenancy_contract = db.Column(db.String(500))
    other_documents = db.Column(db.String(2000))
    txn_no = db.Column(db.String(500))
    txn_date = db.Column(db.String(500))
    txn_amount = db.Column(db.String(500))
    post_status = db.Column(db.String(100))
    kickback_percentage = db.Column(db.String(100))
    kickback_amount = db.Column(db.String(100))
    kickback_status = db.Column(db.String(100))
    agent_commission = db.Column(db.String(50))
    pending_eligible = db.Column(db.String(50))
    ct_percentage = db.Column(db.String(50))
    ct_value = db.Column(db.String(50))
    city = db.Column(db.String(50))
    branch = db.Column(db.String(50))





class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Status = db.Column(db.String(100))
    Employee_Status = db.Column(db.String(100))
    Employee_ID = db.Column(db.String(100))
    Name = db.Column(db.String(100))
    Position = db.Column(db.String(100))
    Nationality = db.Column(db.String(100))
    UID = db.Column(db.String(100))
    Date_of_Birth = db.Column(db.DateTime)
    Date_of_Joining = db.Column(db.DateTime)
    Emirates_ID = db.Column(db.String(100))
    Card_No = db.Column(db.String(100))
    Emirates_Card_Expiry = db.Column(db.DateTime)
    Mobile_No = db.Column(db.String(100))
    MOL_Personal_No = db.Column(db.String(100))
    Labor_Card_No = db.Column(db.String(100))
    Labor_Card_Expiry = db.Column(db.DateTime)
    Insurance_No = db.Column(db.String(100))
    Insurance_Effective_Date = db.Column(db.DateTime)
    Insurance_Expiry_Date = db.Column(db.DateTime)
    Date_of_Submission = db.Column(db.DateTime)
    Residence_Expiry = db.Column(db.DateTime)
    Remarks = db.Column(db.String(100))
    created_by = db.Column(db.String(100))
    pers_no = db.Column(db.String(100))
    company_email = db.Column(db.String(100))
    salary = db.Column(db.String(100))
    slab = db.Column(db.String(100))
    crm_username = db.Column(db.String(100))
    profile_photo = db.Column(db.String(500))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)

class Exitform(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    name = db.Column(db.String(100))
    designation = db.Column(db.String(50))
    department = db.Column(db.String(50))
    date_from = db.Column(db.DateTime)
    date_to = db.Column(db.DateTime)
    time_from = db.Column(db.Time)
    time_to = db.Column(db.Time)
    reason = db.Column(db.String(1000))
    viewing_lead = db.Column(db.String(50))
    manager_approval = db.Column(db.String(50))
    hr_acknowledge = db.Column(db.DateTime)
    hr_approval = db.Column(db.String(50))
    remarks = db.Column(db.String(1000))
    extra01 = db.Column(db.String(500))
    created_by = db.Column(db.String(100))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    branch = db.Column(db.String(50))

class Leaveform(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    name = db.Column(db.String(100))
    designation = db.Column(db.String(50))
    department = db.Column(db.String(50))
    employee_no = db.Column(db.String(50))
    joining_date = db.Column(db.DateTime)
    leave_type = db.Column(db.String(50))
    reason = db.Column(db.String(1000))
    date_from = db.Column(db.DateTime)
    date_to = db.Column(db.DateTime)
    no_of_days = db.Column(db.Integer)
    leave_balance = db.Column(db.Integer)
    manager_ack_date =  db.Column(db.DateTime)
    manager_approval = db.Column(db.String(50))
    hr_ack_date = db.Column(db.DateTime)
    hr_approval = db.Column(db.String(50))
    remarks = db.Column(db.String(1000))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    created_by = db.Column(db.String(50))
    docs = db.Column(db.String(100))
    branch = db.Column(db.String(50))

class Listingdata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    city = db.Column(db.String(50))
    location = db.Column(db.String(50))
    sublocation = db.Column(db.String(50))
    unit_no = db.Column(db.String(50))
    owner_name = db.Column(db.String(500))
    owner_no = db.Column(db.String(50))
    owner_email = db.Column(db.String(100))
    status = db.Column(db.String(50))
    remarks = db.Column(db.String(1000))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    created_by = db.Column(db.String(50))

class Advanceform(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    name = db.Column(db.String(50))
    designation = db.Column(db.String(50))
    department = db.Column(db.String(50))
    employee_no = db.Column(db.String(50))
    request_date = db.Column(db.DateTime)
    com_from = db.Column(db.String(50))
    amount_requested = db.Column(db.String(50))
    salary_month = db.Column(db.String(50))
    reason = db.Column(db.String(1000))
    tl_ack =  db.Column(db.DateTime)
    tl_approval = db.Column(db.String(50))
    manager_ack =  db.Column(db.DateTime)
    manager_approval = db.Column(db.String(50))
    ceo_ack =  db.Column(db.DateTime)
    ceo_approval = db.Column(db.String(50))
    account_ack =  db.Column(db.DateTime)
    account_approval = db.Column(db.String(50))
    remarks = db.Column(db.String(1000))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)
    created_by = db.Column(db.String(50))
    branch = db.Column(db.String(50))

class Maindraft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    name = db.Column(db.String(100))
    number = db.Column(db.String(50))
    role = db.Column(db.String(50))
    location = db.Column(db.String(50))
    community = db.Column(db.String(50))
    type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    draft_status = db.Column(db.String(50))
    draft_location = db.Column(db.String(50))
    draft_community = db.Column(db.String(50))
    draft_type = db.Column(db.String(50))
    source = db.Column(db.String(50))
    lead_refno = db.Column(db.String(50))
    created_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)

class Activedraft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    name = db.Column(db.String(100))
    number = db.Column(db.String(50))
    role = db.Column(db.String(50))
    location = db.Column(db.String(50))
    assign_to = db.Column(db.String(50))
    community = db.Column(db.String(50))
    type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    update_location = db.Column(db.String(50))
    update_community = db.Column(db.String(50))
    update_type = db.Column(db.String(50))
    comment = db.Column(db.String(1000))
    source = db.Column(db.String(50))
    lead_refno = db.Column(db.String(50))
    activated_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)

class Agentlogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    user = db.Column(db.String(50))
    type = db.Column(db.String(50))
    client_name = db.Column(db.String(100))
    client_number = db.Column(db.String(50))
    status = db.Column(db.String(50))
    details = db.Column(db.String(500))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)

class Leadlogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    user = db.Column(db.String(50))
    type = db.Column(db.String(50))
    client_name = db.Column(db.String(100))
    client_number = db.Column(db.String(50))
    status = db.Column(db.String(50))
    source = db.Column(db.String(50))
    details = db.Column(db.String(500))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)

class Leadsdubai(db.Model):
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
    created_date = db.Column(db.DateTime)
    lead_type = db.Column(db.String(50))
    finance_type = db.Column(db.String(50))
    propertyamenities = db.Column(db.String(800))
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
    lastupdated = db.Column(db.DateTime)
    branch = db.Column(db.String(50))
    city = db.Column(db.String(50))

class Contactsdubai(db.Model):
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
    branch = db.Column(db.String(50))

class Transactionad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    user = db.Column(db.String(50))
    deal_ref = db.Column(db.String(50))
    transaction_date = db.Column(db.DateTime)
    type = db.Column(db.String(50))
    mode = db.Column(db.String(50))
    amount = db.Column(db.String(50))
    description = db.Column(db.String(500))
    created_by = db.Column(db.String(50))
    created_date = db.Column(db.DateTime)

class Leadslogsdubai(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    user = db.Column(db.String(50))
    type = db.Column(db.String(50))
    client_name = db.Column(db.String(100))
    client_number = db.Column(db.String(50))
    status = db.Column(db.String(50))
    source = db.Column(db.String(50))
    details = db.Column(db.String(500))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)    

class Maindraftdxb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    name = db.Column(db.String(100))
    number = db.Column(db.String(50))
    role = db.Column(db.String(50))
    location = db.Column(db.String(50))
    community = db.Column(db.String(50))
    type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    draft_status = db.Column(db.String(50))
    draft_location = db.Column(db.String(50))
    draft_community = db.Column(db.String(50))
    draft_type = db.Column(db.String(50))
    source = db.Column(db.String(50))
    lead_refno = db.Column(db.String(50))
    created_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)

class Activedraftdxb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    name = db.Column(db.String(100))
    number = db.Column(db.String(50))
    role = db.Column(db.String(50))
    location = db.Column(db.String(50))
    assign_to = db.Column(db.String(50))
    community = db.Column(db.String(50))
    type = db.Column(db.String(50))
    status = db.Column(db.String(50))
    update_location = db.Column(db.String(50))
    update_community = db.Column(db.String(50))
    update_type = db.Column(db.String(50))
    comment = db.Column(db.String(1000))
    source = db.Column(db.String(50))
    lead_refno = db.Column(db.String(50))
    activated_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)

class Agentlogsdxb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    refno = db.Column(db.String(50))
    user = db.Column(db.String(50))
    type = db.Column(db.String(50))
    client_name = db.Column(db.String(100))
    client_number = db.Column(db.String(50))
    status = db.Column(db.String(50))
    details = db.Column(db.String(500))
    created_date = db.Column(db.DateTime)
    updated_date = db.Column(db.DateTime)