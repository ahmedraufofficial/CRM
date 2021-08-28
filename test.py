'''
x=['Blocked','Pending','Moved In','Pending','Reserved','Sold','Upcoming']

a = []


for i in x:
    
    a.append((i,i))

print(a)

import json
f = open('abudhabi.json')
file_data = json.load(f)
print(file_data['03548'])





import os 

import json
username = 'ahmed'
a = os.getcwd()
UPLOAD_FOLDER = os.path.join(a+'/static/userdata', username)
#if not os.path.isdir(UPLOAD_FOLDER):
#    os.mkdir(UPLOAD_FOLDER)

def write_json(target_file):
    with open(os.path.join(UPLOAD_FOLDER, target_file), 'w') as f:
        data = {}
        data['logs'] = []
        data['reminders'] = []
        json.dump(data, f)

#a = username+'.json'
#write_json(a)
from datetime import datetime

def logs(username,task):
    with open(os.path.join(UPLOAD_FOLDER, username+'.json'),'r+') as file:
        columns = json.load(file)
        now = datetime.now()
        date = now.strftime("%d/%m/%Y")
        time = now.strftime("%H:%M:%S")
        task = task
        columns["logs"].append({
            'date':date,
            'time':time,
            'task':task
        })
        file.seek(0)
        json.dump(columns, file,indent=4)

#logs(username,"chait")
print (os.getcwd()+'/static')

f = open(UPLOAD_FOLDER+'.json')
columns = json.load(f)
con = columns["logs"]
for i in con:
    print(i['date'])

'''
"""
import easyimap

password = "ahmedrauf1"

username = "a.rauf@uhpae.com"

server = easyimap.connect("uhp.uhpae.com", username, password)

email = server.mail(server.listids()[1])

[mail] = server.listup(1)
a = mail.uid
sender,title,body = (lambda data: [data.from_addr, data.title, data.body])(server.mail(str(a)))
if sender in ['noreply@bayut.com', 'bayut3@uhpae.com']:
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
    


from flask import Flaska
from apscheduler.schedulers.background import BackgroundScheduler



count = 0

def sensor():
    global count
    sched.print_jobs()
    print(count)
    count += 1

sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor,'cron',minute='*')


app = Flask(__name__)

@app.route('/')
def shutdown():
    sched.shutdown()
    return 'shutdown'

@app.route('/start')
def start():
    if sched.state == 0:
        sched.start()
    return 'start'

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)

from datetime import datetime,timedelta


now = datetime.now()
date = now.strftime("%d-%m-%Y")
time = now.strftime("%H:%M:%S")
d = date+'T'+time
b = datetime.strptime(d, '%d-%m-%YT%H:%M:%S') + timedelta(hours=2)
USERS_FOLDER = os.getcwd() + '/static/userdata'
available_agents = []
with open(os.path.join(USERS_FOLDER, 'ahmed.json'),'r+') as file:
    columns = json.load(file)
    con = list(columns["leads"].keys())
    print(con)
  
a = "contact_buyer_name = form.contact_buyer_name.data,contact_buyer_number = form.contact_buyer_number.data,contact_buyer_email = form.contact_buyer_email.data,contact_seller = form.contact_seller.data,contact_seller_name = form.contact_seller_name.data,contact_seller_number = form.contact_seller_number.data,contact_seller_email = form.contact_seller_email.data,cheques = cheques"

a = a.split(',')
for i in a:
    print(i.split(' = ')[0] +'='+ i.split(' = ')[0])

  """

a=".csv,text/csv:.doc,application/msword:.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document:.gz,application/gzip:.mp4,video/mp4:.png,image/png:.pdf,application/pdf:.ppt,application/vnd.ms-powerpoint:.pptx,application/vnd.openxmlformats-officedocument.presentationml.presentation:.txt,text/plain:.webp,image/webp:.jpg,image/jpg:.jpeg,image/jpeg"
a= a.split(':')
z = {}
for i in a:
    c,d = i.split(',')
    z.update({c[1:]:d})

print(z) 