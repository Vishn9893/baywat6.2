import os
import pandas as pd
import configparser
import datetime
from sqlalchemy import create_engine
import pytz, json
import requests
from sqlalchemy.sql.expression import false

config = configparser.ConfigParser()
config.read('config.ini')

utc=pytz.timezone('UTC')
tz = pytz.timezone('Europe/Berlin')

# Base config
LAST_TICKET_NUMBER=config['TICKET']['last_ticket_number']
LAST_TICKET_DATE=config['TICKET']['last_ticket_date']
TICKET_TIME_ZONE=config['TICKET']['ticket_time_zone']
if len(LAST_TICKET_DATE) > 0:
    LAST_TICKET_DATE = datetime.datetime.strptime(LAST_TICKET_DATE, '%Y-%m-%d %H:%M:%S')
    LAST_TICKET_DATE = LAST_TICKET_DATE.astimezone(tz)

# ANTARES config
ANTARES_PUBLIC_API=config['ANTARES']['public_api']
ANTARES_ANALYTIC_API=config['ANTARES']['url_analytic_api']
ANTARES_API_KEY=config['ANTARES']['api_key']
ANTARES_API_SECRET=config['ANTARES']['api_secret']

last_ticket_number = ''
last_ticket_date = ''

sql_where = " WHERE 1=1 "
#if len(LAST_TICKET_NUMBER) > 0:
#    sql_where += """ AND "CaseNumber" > '%s' """ % LAST_TICKET_NUMBER
if LAST_TICKET_DATE != '':
    sql_where += """ AND "CreatedDate" > '%s' """ % LAST_TICKET_DATE.strftime('%Y-%m-%d %H:%M:%S.%f%z')

query = """
        SELECT "CaseNumber", "Name", "Plant_Type__c", "Energy_Type__c", "Subject_c", "CreatedDate", "ClosedDate", "Status", "Priority" 
        FROM salesforce_tickets 
        {}
        ORDER BY "CreatedDate" DESC, "CaseNumber" DESC limit 5;
        """.format(sql_where)

engine = create_engine("postgresql://external_user1:6@VNyw5@postgres-aws-test.co6ibupyk0ln.us-west-1.rds.amazonaws.com/baywaaws")
conn = engine.connect()
results = conn.execute(query)
rows = results.fetchall()
conn.close()
# Store last ticket info
if len(rows) >= 1:
    last_ticket_number = rows[0][0]
    last_ticket_date = rows[0][5]
    last_ticket_date = last_ticket_date.astimezone(tz) # Transform datetime to timezone
    last_ticket_date = last_ticket_date.strftime('%Y-%m-%d %H:%M:%S')
    
# Send to ANTARES
request_errors = []

headers = {'Content-Type' : 'application/json; charset=utf-8'}
for row in rows:
    priority = 3
    if row.Priority == 'Low':
        priority = 1
    elif row.Priority == 'Medium':
        priority = 2
    
    to_schedule = False
    if row.Status == 'To be scheduled':
        to_schedule = True

    body_request = {
        "Name" : row.Name,
        "Description" : row.Subject_c,
        "PortfolioId" : config['ANTARES']['porfolio_tag'],
        "CustomerId" : config['ANTARES']['customer_tag'],
        "HelpdeskId" : config['ANTARES']['helpdesk_tag'],
        "ExpectedOperationDate" : row.CreatedDate.strftime('%Y-%m-%d %H:%M:%S'),
        "EmailHeaderConversationTopic" : row.CaseNumber,
        "TicketStatusId" : config['ANTARES']['ticket_status_tag'],
        "ToSchedule" : to_schedule, # Sentire Vish se ok
        "NatureType" : 1,
        "Type" : 1,
        "Source" : 4,
        "Impact" : 2,
        "Priority" : priority,
        "Urgency" : 2,
        "Visible" : True
    }
    body_request = json.dumps(body_request)
    res = requests.post(url=ANTARES_PUBLIC_API, headers=headers, data=body_request, auth=(ANTARES_API_KEY, ANTARES_API_SECRET))
    if res.status_code != 200:
        msg = 'Error {} in the API response'.format(res.status_code)
        request_errors.append(msg)

if len(request_errors) > 0:
    df_request_errors = pd.DataFrame(request_errors)
    if not os.path.isfile('request_errors.csv'):
        df_request_errors.to_csv('request_errors.csv', header='column_names', sep=';')
    else:
        df_request_errors.to_csv('request_errors.csv', mode='a', header=False, sep=';')

# Save last ticket
flag_edits = False
if len(last_ticket_number) > 0:
    config['TICKET']['last_ticket_number']=last_ticket_number
    flag_edits = True
if len(last_ticket_date) > 0:
    config['TICKET']['last_ticket_date']=last_ticket_date
    flag_edits = True

if flag_edits:
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

