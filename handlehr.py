from flask import Blueprint, render_template, request, jsonify, redirect, url_for,abort
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import exc
from sqlalchemy.sql.elements import Null
from models import User, Leaveform, Exitform
from forms import AddPropertyForm, Addlistingdata
import json
import os 
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import re
import glob
from functions import logs, notes, add_user_list
from sqlalchemy import or_, and_
import xml.etree.cElementTree as e
from datetime import datetime, timedelta
import requests
import json
import re
import sqlite3
import os
import csv
import time
from flask_httpauth import HTTPTokenAuth
import pandas as pd
import plotly.graph_objects as go
import socket
import threading

# Configuration
SERVER_HOST = '0.0.0.0'  # Listen on all network interfaces
SERVER_PORT = 9090       # Port on your VPS server
DEST_IP = '192.168.0.19'  # Destination IP on your local network
DEST_PORT = 8085          # Port on 192.168.0.19

def handle_client(client_socket):
    # Connect to the destination server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((DEST_IP, DEST_PORT))
    
    # Forwarding loop
    while True:
        # Receive data from the client
        client_data = client_socket.recv(4096)
        if not client_data:
            break
        # Forward received data to the server
        server_socket.sendall(client_data)
        
        # Receive data from the server
        server_data = server_socket.recv(4096)
        if not server_data:
            break
        # Forward received data back to the client
        client_socket.sendall(server_data)
    
    # Close sockets
    client_socket.close()
    server_socket.close()

def main():
    # Create a socket to accept incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"[*] Listening on {SERVER_HOST}:{SERVER_PORT}")

    try:
        while True:
            client_socket, client_addr = server_socket.accept()
            print(f"[*] Accepted connection from {client_addr[0]}:{client_addr[1]}")
            
            # Handle each client connection in a separate thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    
    finally:
        server_socket.close()

auth = HTTPTokenAuth(scheme='Bearer')
tokens = {
    ''
}

db = SQLAlchemy()
handlehr = Blueprint('handlehr', __name__, template_folder='templates')

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return token

@handlehr.route('/fetch_hr_token',methods = ['GET','POST'])
@login_required
def fetch_txn_token():
    return(jsonify(''))


@handlehr.route('/biotime_auth', methods=['GET', 'POST'])
@login_required
def biotime_auth():
    url = "http://108.167.175.18:9090/jwt-api-token-auth/"
    headers = {"Content-Type": "application/json"}
    data = {"username": "", "password": ""}
    
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return(response.json().get("token"))
    
def biotime_report(emp_id, from_date, to_date):
    token = biotime_auth()
    next = "http://108.167.175.18:9090/iclock/api/transactions/?emp_code="+emp_id+"&start_time="+from_date+"&end_time="+to_date
    m = []
    while next != None:
        new_batch = diff_report_pages(next, token)
        next = new_batch['next']
        m+=new_batch['m_new']
    return(m)

def diff_report_pages(next, token):
    url = next
    headers = {
        "Content-Type": "application/json",
        "Authorization": "JWT "+token
        }
    response = requests.get(url, headers=headers).json()
    m_new = []
    for i in response['data']:
        m_new.append({'type':i['punch_state_display'], 'date':i['punch_time'][:10], 'time':i['punch_time'][11:]})
    next = response['next']
    new_batch = {'next':next, 'm_new':m_new}
    return(new_batch)

def process_data(data):
    df = pd.DataFrame(data)
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    df.sort_values(by=['datetime'], inplace=True)
    
    results = []
    
    # Generate all dates within the date range
    all_dates = pd.date_range(start=df['datetime'].dt.date.min(), end=df['datetime'].dt.date.max())
    
    for date in all_dates:
        date_data = df[df['datetime'].dt.date == date]
        if not date_data.empty:
            date_dict = {'date': date.strftime('%Y-%m-%d')}
            events = []
            for idx, row in date_data.iterrows():
                current_time = row['datetime'].time()
                if row['type'] == 'Check In':
                    events.append({
                        'time': current_time.strftime('%H:%M'),
                        'event': 'Check In'
                    })
                elif row['type'] == 'Check Out':
                    events.append({
                        'time': current_time.strftime('%H:%M'),
                        'event': 'Check Out'
                    })
            date_dict['events'] = events
            results.append(date_dict)
        else:
            # Add None record for dates without data
            results.append({
                'date': date.strftime('%Y-%m-%d'),
                'events': None
            })
    
    return results

def create_graph(data):
    fig = go.Figure()
    y_tickvals = []  # List to store y-axis tick values
    absent = 0
    late = 0
    
    for item in data:
        date_str = item['date']
        events = item['events']

        if events is None:
            absent+=1
            # Add red dashed line for days with no attendance data
            fig.add_trace(go.Scatter(
                x=[datetime.strptime('09:00', '%H:%M').strftime('%Y-%m-%d %H:%M'), datetime.strptime('18:00', '%H:%M').strftime('%Y-%m-%d %H:%M')],
                y=[date_str, date_str],
                mode='lines',
                line=dict(color='red', dash='dash'),  # Red dashed line for days with no records
                name=None  # No legend entry
            ))
            y_tickvals.append(date_str) 
            continue  # Skip to the next item if events are None

        # Find the earliest check-in time for the day
        check_in_times = [datetime.strptime(event['time'], '%H:%M') for event in events if event['event'] == 'Check In']
        if check_in_times:
            earliest_check_in_time = min(check_in_times)
        else:
            earliest_check_in_time = None

        # Add yellow line from 09:15 to earliest check-in time if it exists
        if earliest_check_in_time and earliest_check_in_time.time() > datetime.strptime('09:15', '%H:%M').time():
            late += 1
            fig.add_trace(go.Scatter(
                x=[datetime.strptime('09:15', '%H:%M').strftime('%Y-%m-%d %H:%M'), earliest_check_in_time.strftime('%Y-%m-%d %H:%M')],
                y=[date_str, date_str],
                mode='lines',
                line=dict(color='yellow'),
                name=None,  # No legend entry
            ))

        check_in_time = None
        for event in events:
            event_type = event['event']
            time_str = event['time']
            event_dt = datetime.strptime(time_str, '%H:%M')

            if event_type == 'Check In':
                if check_in_time is None:
                    check_in_time = event_dt
                    try:
                        if check_out_time_previous.time() < check_in_time.time():
                            fig.add_trace(go.Scatter(
                                x=[check_out_time.strftime('%Y-%m-%d %H:%M'), check_in_time.strftime('%Y-%m-%d %H:%M')],
                                y=[date_str, date_str],
                                mode='lines',
                                line=dict(color='red'),  # Red line for check-outs to check-ins
                                name=None  # No legend entry
                            ))
                    except:
                        pass
            elif event_type == 'Check Out':
                if check_in_time:
                    check_out_time = event_dt
                    fig.add_trace(go.Scatter(
                        x=[max(check_in_time, datetime.strptime('09:00', '%H:%M')).strftime('%Y-%m-%d %H:%M'), 
                           min(check_out_time, datetime.strptime('18:00', '%H:%M')).strftime('%Y-%m-%d %H:%M')],
                        y=[date_str, date_str],
                        mode='lines',
                        line=dict(color='green'),  # Green line for check-in to check-out interval
                        name=None  # No legend entry
                    ))
                    
                    # Add red line between check-outs and check-ins for the same day
                    check_out_time_previous = check_out_time
                    check_in_time = None
            else:
                # Example for other event types
                fig.add_trace(go.Scatter(
                    x=[event_dt.strftime('%Y-%m-%d %H:%M'), event_dt.strftime('%Y-%m-%d %H:%M')],
                    y=[date_str, date_str],
                    mode='lines',
                    line=dict(color='blue'),  # Blue line for other event types
                    name=None  # No legend entry
                ))

        # If check-in is present but no corresponding check-out, extend the line till 18:00
        if check_in_time:
            fig.add_trace(go.Scatter(
                x=[max(check_in_time, datetime.strptime('09:00', '%H:%M')).strftime('%Y-%m-%d %H:%M'), 
                   datetime.strptime('18:00', '%H:%M').strftime('%Y-%m-%d %H:%M')],
                y=[date_str, date_str],
                mode='lines',
                line=dict(color='blue'),  # Green line till 18:00 for check-ins without check-outs
                name=None  # No legend entry
            ))

        # Add date to y-axis tick values if not already present
        if date_str not in y_tickvals:
            y_tickvals.append(date_str)

    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Date',
        showlegend=False,  # Remove legends
        height=700,  # Set the height of the graph (adjust as needed)
        xaxis=dict(
            tickmode='linear',
            tick0=datetime.strptime('09:00', '%H:%M').strftime('%Y-%m-%d %H:%M'),
            dtick=3600000,  # 1 hour in milliseconds
            tickformat='%H:%M',
            side='top',  # Label only one side of the x-axis
            range=[
                datetime.strptime('09:00', '%H:%M').strftime('%Y-%m-%d %H:%M'),
                datetime.strptime('18:00', '%H:%M').strftime('%Y-%m-%d %H:%M')
            ]
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=y_tickvals,
            tickformat='%m-%d  %a '
        )
    )
    return fig.to_dict()['data'], fig.to_dict()['layout'], late, absent

@handlehr.route('/hr_report')
@login_required
def hr_report():
    f = open('attendance_headers.json')
    columns = json.load(f)
    col_exit = columns["headers_exit"]
    col_leave = columns["headers_leave"]
    return render_template('hr_report.html',col_exit = col_exit, col_leave = col_leave)

@handlehr.route('/attendance_sheet')
@auth.login_required
def attendance_sheet():
    filters_01 = {key: request.args.get(key) for key in request.args}
    filters = {key: filters_01[key] for key in ['emp_code','propdate', 'propdate2'] if key in filters_01}

    today = datetime.today()
    first_of_month = today.replace(day=1)
    last_of_month = (first_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    from_date = first_of_month.strftime('%Y-%m-%d')
    to_date = last_of_month.strftime('%Y-%m-%d')
    emp_code = '1148'

    for key, value in filters.items():
        if key == 'propdate':
            from_date = value
        elif key == 'propdate2':
            value_as_datetime = datetime.strptime(value, '%Y-%m-%d')
            value_as_datetime += timedelta(days=1)
            value = value_as_datetime.strftime('%Y-%m-%d')
            to_date = value
        else:
            emp_code = value

    voltage_user = db.session.query(User).filter(User.emp_code == emp_code).first()

    data = biotime_report(emp_code, from_date, to_date)
    processed_data = process_data(data)
    graph_data, graph_layout, late, absent = create_graph(processed_data)

    data_1 = []
    data_2 = []
    for r in db.session.query(Leaveform).filter(or_((and_(Leaveform.date_from >= from_date, Leaveform.date_from <= to_date, Leaveform.created_by == voltage_user.username)),(and_(Leaveform.date_to >= from_date, Leaveform.date_to <= to_date, Leaveform.created_by == voltage_user.username)))):
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
            data_1.append(new)
    for r in db.session.query(Exitform).filter(or_((and_(Exitform.date_from >= from_date, Exitform.date_from <= to_date, Exitform.created_by == voltage_user.username)),(and_(Exitform.date_to >= from_date, Exitform.date_to <= to_date, Exitform.created_by == voltage_user.username)))):
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
            data_2.append(new)
    f = open('attendance_headers.json')
    columns = json.load(f)
    col_exit = columns["headers_exit"]
    col_leave = columns["headers_leave"]
    return jsonify(graph_data=graph_data, graph_layout=graph_layout, absent = absent, late = late, data_1 = data_1, data_2 = data_2,col_exit = col_exit, col_leave = col_leave, voltage_user = voltage_user.username)