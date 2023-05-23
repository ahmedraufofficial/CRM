from models import Leads
import os 
import json
from datetime import datetime, timedelta
import random
import easyimap
import smtplib
import requests
#from twilio.rest import Client
#from twilio.base.exceptions import TwilioRestException

#account_sid = ""
#auth_token = ""


USERS_FOLDER = os.getcwd() + '/static/userdata'
NOTES = os.getcwd() + '/static/notes'
SCHEDULER = os.getcwd() + '/static/scheduler'


def lead_email(email, lead):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("uhpaeworldwide@gmail.com","Uhp@421907")
        message = lead+" Has been assigned to you! Kindly follow up."
        server.sendmail("uhpaeworldwide@gmail.com", email, message)
        server.quit
        print('done')
    except:
        pass
       



def create_json(username):
    username = username.replace("%20"," ")
    with open(os.path.join(USERS_FOLDER,username+'.json'), 'w') as f:
        data = {}
        data['logs'] = []
        data['reminders'] = []
        data['lead'] = {}
        data['list'] = {}
        json.dump(data, f)


def logs(username,ref,task):
    username = username.replace("%20"," ")
    task = task.replace("%20"," ")
    with open(os.path.join(USERS_FOLDER, username+'.json'),'r+') as file:
        columns = json.load(file)
        now = datetime.now()+timedelta(hours=4)
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")
        task = task
        columns["logs"].append({
            'date':date,
            'time':time,
            'ref':ref,
            'task':task
        })
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()

def post_reminders(username,from_date,to_date,from_time,to_time,title):
    username = username.replace("%20"," ")
    title = title.replace("%20"," ")
    from_date = from_date.replace("%20"," ")
    to_date = to_date.replace("%20"," ")
    from_time = from_time.replace("%20"," ")
    to_time = to_time.replace("%20"," ")
    with open(os.path.join(USERS_FOLDER, username+'.json'),'r+') as file:
        columns = json.load(file)
        start = str(from_date+'T'+from_time+':00')
        end = str(to_date+'T'+to_time+':00')
        id = str(len(columns['reminders'])+1)
        columns["reminders"].append({
          'id' :id,
          'title':title,
          'start':start,
          'end' :end
        })
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()

def reminders(username):
    username = username.replace("%20"," ")
    with open(os.path.join(USERS_FOLDER, username+'.json'),'r+') as file:
        columns = json.load(file)
        return(columns['reminders'])
      

def get_log(username):
    username = username.replace("%20"," ")
    f = open(os.path.join(USERS_FOLDER, username+'.json'))
    columns = json.load(f)
    con = columns["logs"]
    return con
        
def notes(listid):
    with open(os.path.join(NOTES,listid+'.json'), 'w') as f:
        data = {}
        data['notes'] = []
        json.dump(data, f)

def additional_details(listid):
    with open(os.path.join(NOTES,listid+'.json'), 'w') as f:
        data = {}
        data['notes'] = []
        json.dump(data, f)

def get_notes(listid):
    f = open(os.path.join(NOTES,listid+'.json'))
    columns = json.load(f)
    con = columns["notes"]
    return con

def update_note(username, listid, com):
    username = username.replace("%20"," ")
    com = com.replace("%20"," ")
    with open(os.path.join(NOTES, listid+'.json'),'r+') as file:
        columns = json.load(file)
        a = columns['notes']
        now = datetime.now()+timedelta(hours=4)
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")
        columns["notes"].append({
            'date':date,
            'time':time,
            'user':username,
            'comment': com
        })
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()

def update_detail(list_id,detail,val):
    val = val.replace("%20"," ")
    detail = detail.replace("%20"," ")
    with open(os.path.join(NOTES, list_id+'.json'),'r+') as file:
        columns = json.load(file)
        a = columns['notes']
        now = datetime.now()+timedelta(hours=4)
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")
        columns["notes"].append({
            'date':date,
            'time':time,
            'detail':detail,
            'value': val,
            'options':'<a href="/delete_detail/'+list_id+'/'+detail+'"><button class="btn btn-danger si">Delete</button></a>'
        })
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()

def del_detail(list_id,detail):
    detail = detail.replace("%20"," ")
    with open(os.path.join(NOTES, list_id+'.json'),'r+') as file:
        columns = json.load(file)
        a = columns['notes']
        for i in a:
            if i["detail"] == detail:
                columns['notes'].remove(i)
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()

def update_lead_note(username, listid, com, status, substatus):
    username = username.replace("%20"," ")
    com = com.replace("%20"," ")
    substatus = substatus.replace("%20"," ")
    with open(os.path.join(NOTES, listid+'.json'),'r+') as file:
        columns = json.load(file)
        now = datetime.now()+timedelta(hours=4)
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")
        columns["notes"].append({
            'date':date,
            'time':time,
            'user':username,
            'comment': com,
            'status': status,
            'substatus': substatus
        })
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()

def get_lead():
    password = "ahmedrauf1"
    username = "a.rauf@uhpae.com"
    server = easyimap.connect("uhp.uhpae.com", username, password)
    [mail] = server.listup(1)
    a = mail.uid
    sender,title,body = (lambda data: [data.from_addr, data.title, data.body])(server.mail(str(a)))
    if sender in ['noreply@bayut.com', 'bayut@uhpae.com']:
        for i in ['rent', '-r-']:
            if i in title.lower():
                category = "rent"
        for i in ['sale','-s-']:
            if i in title.lower():
                category = "sale"
        message, prop_details = (lambda data: [data.split('\r\nINQUIRY MESSAGE\r\n')[1].split('\r\n')[1],data.split('\r\nINQUIRER DETAILS\r\n')[1].split('\r\n')[1:4] + data.split('\r\nPROPERTY DETAILS\r\n')[1].split('\r\n')[1:6]])(body)
        d = {}
        for i in prop_details:
            p = (lambda x: d.update({x[0]:x[1]}))(i.replace(': ',':').split(':'))
        d['Phone'] = d['Phone'].replace('-','').split(' ')[0] 
        leadObj = {}
        leadObj['refno'] = d['Reference']
        leadObj['contact_name'] = d['Name']
        leadObj['contact_number'] = d['Phone']
        leadObj['contact_email'] = d['Email']
        leadObj['message'] = message
        return leadObj

    if sender in ['noreply23@email.dubizzle.com']:
        for i in ['rent', '-r-']:
            if i in title.lower():
                category = "rent"
        for i in ['sale','-s-']:
            if i in title.lower():
                category = "sale"
        message, prop_details = (lambda data: [data.split('Message:')[1].split('\r\n\r\n')[0].replace('\n','').replace('\r','')[1:], data.split('Ref ')[1].split('\r\n')[0:4]])(body)
        d = {}
        for i in prop_details:
            p = (lambda x: d.update({x[0]:x[1]}))(i.replace(': ',':').split(':'))
        d['Telephone'] = d['Telephone'].split(' ')[0] 
        leadObj = {}
        leadObj['refno'] = d['No']
        leadObj['contact_name'] = d['Name']
        leadObj['contact_number'] = d['Telephone']
        leadObj['contact_email'] = d['Email']
        leadObj['message'] = message
        return leadObj

def getAvailableAgents(usernames,leads):
    now = datetime.now()+timedelta(hours=4)
    from_date = now.strftime("%Y-%m-%d")
    from_time = now.strftime("%H:%M")
    expiry_now = datetime.now()+timedelta(hours=4) + timedelta(hours=2)
    to_date = expiry_now.strftime("%Y-%m-%d")
    to_time = expiry_now.strftime("%H:%M")
    available_agents = []
    assigned = []
    no_follow_up = []
    for username in usernames:
        f = open(os.path.join(USERS_FOLDER, username+'.json'))
        columns = json.load(f)
        con = list(columns["lead"].keys())
        if not con:
            available_agents.append(username)
        else:
            check = True
            for i in con:
                if columns["lead"][i]["status"] == 'Lost' or columns["lead"][i]["status"] == 'Closed':
                    pass
                else:
                    check = False
                print(i)
                if columns["lead"][i]["sub_status"] == "In progress" and columns["lead"][i]["status"] != "Lost":
                    d = columns["lead"][i]["expiry date"] +'T'+ columns["lead"][i]["expiry time"]+":00"
                    b = datetime.strptime(d, '%Y-%m-%dT%H:%M:%S')
                    if b < datetime.now()+timedelta(hours=4):
                        no_follow_up.append((i,username))
            if check == True:
                available_agents.append(username)    
    print(available_agents)
    for lead in leads:
        for username in available_agents:
            with open(os.path.join(USERS_FOLDER, username+'.json'),'r+') as file:
                columns = json.load(file)
                if lead in list(columns["lead"].keys()):
                    continue
                columns["lead"].update({lead:{
                'date':from_date,
                'time':from_time,
                'expiry date':to_date,
                'expiry time':to_time,
                'status':'Open',
                'sub_status':'In progress'
                }})
                file.seek(0)
                json.dump(columns, file,indent=4)
                file.truncate()
            title = lead+' Assigned' 
            print('added to note')
            post_reminders(username,from_date,to_date,from_time,to_time,title)
            assigned.append((lead,username))
            break
    print(assigned)
    return assigned, no_follow_up
        
def assign_lead(username,lead,substatus):
    substatus = substatus.replace("%20"," ")
    f = open(os.path.join(SCHEDULER,'scheduler.json'))
    c = json.load(f)
    c = c['time']

    with open(os.path.join(USERS_FOLDER, username+'.json'),'r+') as file:
        columns = json.load(file)
        now = datetime.now()+timedelta(hours=4)
        from_date = now.strftime("%Y-%m-%d")
        from_time = now.strftime("%H:%M")
        expiry_now = datetime.now()+timedelta(hours=4)
        to_date = expiry_now.strftime("%Y-%m-%d")
        to_time = expiry_now.strftime("%H:%M")
        columns["lead"].update({lead:{
        'date':from_date,
        'time':from_time,
        'expiry date':to_date,
        'expiry time':to_time,
        'status': 'Open',
        'sub_status': substatus
        }})
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate

def lost_lead(username,lead):
    username = username.replace("%20"," ")
    lead = lead.replace("%20"," ")
    with open(os.path.join(USERS_FOLDER, username+'.json'),'r+') as file:
        columns = json.load(file)
        columns["lead"][lead]["status"] = "Lost"
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()

def update_user_note(username,lead,status,sub_status):
    username = username.replace("%20"," ")
    lead = lead.replace("%20"," ")
    status = status.replace("%20"," ")
    sub_status = sub_status.replace("%20"," ")
    with open(os.path.join(USERS_FOLDER, username+'.json'),'r+') as file:
        columns = json.load(file)
        try:
            columns["lead"][lead]["sub_status"] = sub_status
            columns["lead"][lead]["status"] = status
        except:
            now = datetime.now()+timedelta(hours=4)
            from_date = now.strftime("%Y-%m-%d")
            from_time = now.strftime("%H:%M")
            expiry_now = datetime.now()+timedelta(hours=4)
            to_date = expiry_now.strftime("%Y-%m-%d")
            to_time = expiry_now.strftime("%H:%M")
            columns["lead"].update({lead:{
                'date':from_date,
                'time':from_time,
                'expiry date':to_date,
                'expiry time':to_time,
                'status':status,
                'sub_status':sub_status
                }})
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()

def add_user_list(username,list_id):
    username = username.replace("%20"," ")
    list_id = list_id.replace("%20"," ")
    with open(os.path.join(USERS_FOLDER, username+'.json'),'r+') as file:
        now = datetime.now()+timedelta(hours=4)
        from_date = now.strftime("%Y-%m-%d")
        from_time = now.strftime("%H:%M")
        columns = json.load(file)
        columns["list"].update({list_id:{
                'date':from_date,
                'time':from_time,
                }})
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()

def chart_data(chart, username):
    username = username.replace("%20"," ")
    colors = ['rgba(255, 99, 132, 0.2)','rgba(255, 159, 64, 0.2)','rgba(255, 205, 86, 0.2)','rgba(75, 192, 192, 0.2)','rgba(54, 162, 235, 0.2)','rgba(153, 102, 255, 0.2)','rgba(201, 203, 207, 0.2)']
    borderColor = ['rgb(255, 99, 132)','rgb(255, 159, 64)','rgb(255, 205, 86)','rgb(75, 192, 192)','rgb(54, 162, 235)','rgb(153, 102, 255)','rgb(201, 203, 207)']
    f = open(os.path.join(USERS_FOLDER, username+'.json'))
    columns = json.load(f)
    if chart == '1':
        labels = []
        data = []
        bg = []
        bd = []
        for i in columns["lead"]:
            if columns["lead"][i]["status"] == 'Lost' or columns["lead"][i]["status"] == 'Closed':
                exp = columns["lead"][i]["expiry date"] +'T'+ columns["lead"][i]["expiry time"]+":00"
                exp = datetime.strptime(exp, '%Y-%m-%dT%H:%M:%S')
            else:
                exp = datetime.now()+timedelta(hours=4)
            start = columns["lead"][i]["date"] +'T'+ columns["lead"][i]["time"]+":00"
            start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
            labels.append(i)
            data.append(((exp - start).seconds//3600))
            bg.append(random.choice(colors))
            bd.append(random.choice(borderColor))
        return labels,data,bg,bd,"bar"
    
    if chart == '2':
        labels = ['January','February','March','April','May','June','July','August','September','October','November','December']
        all = [0,0,0,0,0,0,0,0,0,0,0,0]
        lost = [0,0,0,0,0,0,0,0,0,0,0,0]
        bg = []
        bd = []
        for i in columns["lead"]:
            m = columns["lead"][i]["date"]
            m = datetime.strptime(m, '%Y-%m-%d')
            z = int(m.month)
            all[z-1] = all[z-1] + 1
            if columns["lead"][i]["status"] == "Lost":
                lost[z-1] = lost[z-1] + 1
        current_m = int(datetime.today().month)
        labels = labels[:current_m]
        data = [all[:current_m],lost[:current_m]]
        return labels,data,"","","lead"
    
    if chart == '3':
        labels = ['January','February','March','April','May','June','July','August','September','October','November','December']
        all = [0,0,0,0,0,0,0,0,0,0,0,0]
        bg = []
        bd = []
        for i in columns["list"]:
            m = columns["list"][i]["date"]
            m = datetime.strptime(m, '%Y-%m-%d')
            z = int(m.month)
            all[z-1] = all[z-1] + 1
        current_m = int(datetime.today().month)
        labels = labels[:current_m]
        data = all[:current_m]
        return labels,data,"","","list"

def update_sch(x):
    with open(os.path.join(SCHEDULER,'scheduler.json'),'r+') as file:
        columns = json.load(file)
        columns.clear()
        columns.update({"time":str(x)})
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()

def get_commission(role, cost, type):
    commission = 0
    if role == "list":
        if cost >= 0 and cost <= 30000:
            commission = 2
        elif cost > 30000 and cost <= 75000:
            commission = 3
        elif cost > 75000 and cost <= 135000:
            commission = 4
        elif cost > 135000:
            commission = 5
    if role == "sale" and type == "Primary":
        if cost > 30000 and cost <= 75000:
            commission = 15
        elif cost > 75000 and cost <= 135000:
            commission = 25
        elif cost > 135000:
            commission = 35
    if role == "sale" and type == "Secondary":
        if cost > 30000 and cost <= 75000:
            commission = 13
        elif cost > 75000 and cost <= 135000:
            commission = 22
        elif cost > 135000:
            commission = 30
    return commission

def viewings(username,lead,status,min_price,max_price,min_room,max_room,area,specific_area):
    with open(os.path.join(os.getcwd(),'viewing.json'),'r+') as file:
        columns = json.load(file)
        columns["viewings"].append({
            'id':len(columns["viewings"])+1,
            'username':username,
            'status':status,
            'lead':lead,
            'datetime':str(datetime.now()+timedelta(hours=4)),
            'min_price':min_price,
            'max_price':max_price,
            'min_room':min_room,
            'max_room':max_room,
            'area':area,
            'specific_area':specific_area,
            'assigned':"<button class='btn btn-success' data-toggle='modal' data-target='#myModal' onclick='assign("+'"'+str(len(columns["viewings"])+1)+'","'+lead+'"'+")'>Assign</button>"
        })
        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate() 
       
def assign_viewing(current,lead_id,lead,lists):
    with open(os.path.join(os.getcwd(),'viewing.json'),'r+') as file:
        columns = json.load(file)
        for i in columns["viewings"]:
            if i["id"] == int(lead_id):
                i["status"] = "Assigned"
                username = i["username"]
                listid = i["lead"]

        file.seek(0)
        json.dump(columns, file,indent=4)
        file.truncate()
        for i in lists.split(","):
            update_note(username, i, "Assigned a viewing by "+current+" : Awaiting Feedback")
            update_lead_note(current, listid, "Assigned Viewing for "+i, "Awating Feedback", "-")
        date = datetime.now()+timedelta(hours=4).strftime("%Y-%m-%d")
        end_date = (datetime.now()+timedelta(hours=4) + timedelta(days=1)).strftime("%Y-%m-%d")
        time = datetime.now()+timedelta(hours=4).strftime("%H:%M")
        post_reminders(username,date,end_date,time,time,"Viewing assigned for "+lead)
        

#def deploy_message(agentname,contactname,agentno,contactno,refno,location,building,leadtype):
#    client = Client(account_sid, auth_token)

#    if(int(str(agentno)[:2]) == 97):
#        e1 = "+"+str(agentno)
#        e2 = "0"+str(agentno)[3:]
#    elif(int(str(agentno)[:1]) == 5):
#        e1 = "+971"+str(agentno)
#        e2 = "0"+str(agentno)
#    else:
#        e1 = "+"+str(agentno)
#        e2 = e1
#
#   if(int(str(contactno)[:2]) == 97):
#        d1 = "+"+str(contactno)
#        d2 = "0"+str(contactno)[3:]
#    elif(int(str(contactno)[:1]) == 5):
#        d1 = "+971"+str(contactno)
#        d2 = "0"+str(contactno)
#    else:
#        d1 = "+"+str(contactno)
#        d2 = d1
#        e2 = e1
#
#    try:
#        message1 = client.messages.create(
#            to=d1,
#            from_="+16266693482",
#            body="Dear Client, Please contact our Agent. "+str(agentname).upper()+" on "+e2+" regarding the property in "+str(building)+", "+str(location)+". Your Ref no. is: "+refno+"."
#            )
#    except TwilioRestException as err:
#        pass
#    try:
#        message2 = client.messages.create(
#            to=e1,
#            from_="+16266693482",
#            body="Dear Agent, Please contact your lead "+str(contactname)+" on "+d2+" regarding the property for "+leadtype+" in "+str(building)+", "+str(location)+". The Ref no. is: "+refno
#            )
#    except TwilioRestException as err:
#        pass

def etisy_message(agentname,contactname,agentno,contactno,refno,location,building,leadtype):
    url = "https://smartmessaging.etisalat.ae:5676/login/user"
    payload = json.dumps({
        "username": "",
        "password": ""
        })
    headers = {
        'Content-Type': 'application/json'
        }
    response = requests.request("POST", url, headers=headers, data=payload)
    x = json.loads(response.text)

    if(int(str(agentno)[:2]) == 97):
        e1 = str(agentno)
        e2 = "0"+str(agentno)[3:]
    elif(int(str(agentno)[:1]) == 5):
        e1 = "971"+str(agentno)
        e2 = "0"+str(agentno)
    elif(int(str(agentno)[:1]) == 0):
        e1 = "971"+str(agentno[1:])
        e2 = str(agentno)
    else:
        e1 = "+"+str(agentno)
        e2 = e1
        
    if(int(str(contactno)[:2]) == 97):
        d1 = str(contactno)
        d2 = "0"+str(contactno)[3:]
    elif(int(str(contactno)[:1]) == 5):
        d1 = "971"+str(contactno)
        d2 = "0"+str(contactno)
    elif(int(str(contactno)[:1]) == 0):
        d1 = "971"+str(contactno[1:])
        d2 = str(contactno)
    else:
        d1 = "+"+str(contactno)
        d2 = d1
        e2 = e1
    body1="Thank you for choosing UHPAE. Our agent "+str(agentname).upper()+" will contact you shortly. Agent contact No. "+e2+"." 
    body2="Dear Agent, Please contact your lead "+str(contactname)+" on "+d2+" regarding the property for "+leadtype+" in "+str(building)+", "+str(location)+". The Ref no. is: "+refno
    #launch_that_message(number=d1, message=body1, token=x['token'])
    #launch_that_message(number=e1, message=body2, token=x['token'])
    return(response)

def launch_that_message(number, message, token):
    url = "https://smartmessaging.etisalat.ae:5676/campaigns/submissions/sms/nb/"
    payload = json.dumps({
    "msgCategory": "4.6",
    "contentType": "3.1",
    "senderAddr": "AD-UHP",
    "dndCategory": "Campaign",
    "priority": 1,
    "recipient": number,
    "msg": message
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+token
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)

def etisy_message01():
    url = "https://smartmessaging.etisalat.ae:5676/login/user"
    payload = json.dumps({
        "username": "",
        "password": ""
        })
    headers = {
        'Content-Type': 'application/json'
        }
    response = requests.request("POST", url, headers=headers, data=payload)
    x = json.loads(response.text)
    
    return(x)    
