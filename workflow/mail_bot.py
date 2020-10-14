# log = Logger.get_instance()
import json
import os
from datetime import datetime
from sys import exit

import cx_Oracle
import pandas as pd

# from utils.logger import Logger
from utils.mail import Mail

# from apps.api_and_database import API
current_time = datetime.now()
current_time_string = current_time.strftime("%b %d %Y %H:%M:%S")
condition = None
start_time = None
end_time = None
print(current_time.hour, type(current_time.hour))

if current_time.hour == 7:
    start_time = f"{str(current_time.year)}-{str(current_time.month)}-{str(current_time.day)} 00:00:00"
    end_time = f"{str(current_time.year)}-{str(current_time.month)}-{str(current_time.day)} 07:00:00"

elif current_time.hour == 13:
    start_time = f'{str(current_time.year)}-{str(current_time.month)}-{str(current_time.day)} 07:00:00'
    end_time = f'{str(current_time.year)}-{str(current_time.month)}-{str(current_time.day)} 13:00:00'

elif current_time.hour == 20:
    start_time = f"{str(current_time.year)}-{str(current_time.month)}-{str(current_time.day)} 13:00:00"
    end_time = f"{str(current_time.year)}-{str(current_time.month)}-{str(current_time.day)} 20:00:00"

elif current_time.hour == 0:
    start_time = f"{str(current_time.year)}-{str(current_time.month)}-{str(current_time.day - 1)} 20:00:00"
    end_time = f"{str(current_time.year)}-{str(current_time.month)}-{str(current_time.day)} 00:00:00"

else:
    start_time = input('give start time in formate of YYYY-MM-DD HH24:MI:SS ')
    end_time = input('give end time in formate of YYYY-MM-DD HH24:MI:SS ')

condition = f"create_time > TO_DATE('{start_time}', 'YYYY-MM-DD HH24:MI:SS') and create_time <= TO_DATE('{end_time}', 'YYYY-MM-DD HH24:MI:SS')"
print(f"condition: {condition}")
df = None

try:
    dsn_tns = cx_Oracle.makedsn('raxdw-scan', 1628, service_name='DBC3')
    conn = cx_Oracle.connect(user='rpa', password='bi4#VnPh', dsn=dsn_tns)
    if start_time is None:
        exit(1)
    sql = f"SELECT * FROM RPA.CRM_DV_ERASE_VOUCHER where {condition}"
    df = pd.read_sql(sql, con=conn)

except cx_Oracle.DatabaseError as e:
    print(e)
    # log.log_critical("There is a problem with Oracle DETAILS : EXCEPTION - {e}")

location = './erased_voucher_report.xlsx'

try:
    os.remove(location)
except FileNotFoundError as e:
    # log.log_warn(f"No File Found to be deleted LOCATION - {location}")
    pass

if len(df) > 0:
    df.to_excel(location)
else:
    location = None

mail = Mail(channel=Mail.outlook)
with open('./erased_voucher_config.json') as config_file:
    data = json.load(config_file)
targets = data['targets']
cc = data['cc']
mail_body = f'<p>Dear Concern,</p> {len(df)} number of SR has been processed between {start_time} to {end_time} <p>Thanks</p>'
mail.send_mail_to(targets, cc, 'CRM RPA Report', mail_body, location)
mail.send()
