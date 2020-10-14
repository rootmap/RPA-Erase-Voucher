import os

import cx_Oracle
import pandas as pd

df = None

try:
    dsn_tns = cx_Oracle.makedsn('raxdw-scan', 1628, service_name='DBC3')
    conn = cx_Oracle.connect(user='rpa', password='bi4#VnPh', dsn=dsn_tns)
    # sql = "SELECT * FROM RPA.crm_complain_list order by CREATE_TIME desc"
    # sql = "SELECT * FROM RPA.crm_complain_list where COUNTER_LOG LIKE '%Complain can not close%' and CREATE_TIME >= TO_DATE('2020-01-30 00:00:00','YYYY-MM-DD HH24:MI:SS') order by CREATE_TIME desc "
    # sql = "SELECT * FROM RPA.crm_complain_list WHERE SR_NUMBER in ('20012727607993934','20012727609271780','20012727609300533','20012727609869587','20012727610094341','20012727610104192','20012727610182381','20012727610186442','20012727610305117','20012727610363033','20012727610372284','20012727610462512','20012727610533408','20012727610630996','20012727612037055','20012727612099162','20012727612127861','20012727612148271','20012727612168999','20012727612169081','20012727612248305','20012727612936589','20012727613632278','20012727613658020','20012727613694865','20012727613706977','20012727614980561','20012727614996240','20012727615009823','20012727615059374','20012727615077491','20012727615084491','20012727615092197','20012727615147631','20012727615156861')"
    # sql = "SELECT * FROM RPA.crm_complain_list WHERE PRICE = 'None' and LIST_TYPE = 'white' order by CREATE_TIME desc"
    from datetime import datetime

    current_time = datetime.now()
    sql = "SELECT * FROM RPA.crm_complain_list WHERE CREATE_TIME > TO_DATE('2020-02-02 20:00:00','YYYY-MM-DD HH24:MI:SS')    order by CREATE_TIME desc"
    # sql = f"SELECT * FROM RPA.crm_complain_list WHERE create_time > TO_DATE('{str(current_time.year)}-{str(current_time.month)}-{str(current_time.day-1)} 20:00:00', 'YYYY-MM-DD HH24:MI:SS') and create_time <= TO_DATE('{str(current_time.year)}-{str(current_time.month)}-{str(current_time.day)} 00:00:00', 'YYYY-MM-DD HH24:MI:SS')"

    df = pd.read_sql(sql, con=conn)

except cx_Oracle.DatabaseError as e:
    print(e)
print(df)
print(len(df))
location = 'C:/Users/rashid.rayhan/Desktop/report.csv'
try:
    os.remove(location)
except FileNotFoundError as e:
    # log.log_warn(f"No File Found to be deleted LOCATION - {location}")
    pass

df.to_csv('C:/Users/rashid.rayhan/Desktop/report.csv')
