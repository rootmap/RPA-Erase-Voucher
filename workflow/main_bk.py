import json
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import time
import os
import glob as gb
from dateutil.relativedelta import relativedelta
from apps.encryption import CryptoPassPhase
from pages.pages_xml_wrapper import XMLWrapper
from apps import database


# import datetime as dt
# from utils.logger import Logger
# import cx_Oracle
#
# log = Logger.get_instance()
#
# msisdn = '01860748020'
# dataToInsert = [
#     (10, '01860748020'),
#     (20, '01860748020'),
#     (30, '01860748020'),
#     (40, '01860748020'),
#     (50, '01860748020')
# ]
# Query = "insert into RPA_DIV_ERASE_VOUCHER (COMPLAIN_ID, MSISDN) values (:1, :2)"
# db.executeManyQuery(Query=Query, param=dataToInsert)

# sql = f"SELECT * FROM RPA_DIV_ERASE_VOUCHER ORDER BY ID DESC"
# totalRows = db.selectSingleRow(Query=sql)
# print('Single Rows = ', totalRows)

# sql = f"SELECT * FROM RPA_DIV_ERASE_VOUCHER ORDER BY ID DESC"
# db.selectSingleRow(Query=sql)

# sql = f"SELECT * FROM RPA_DIV_ERASE_VOUCHER ORDER BY ID DESC" db.selectQuery(Query=sql) sql = f"""INSERT INTO
# RPA_DIV_ERASE_VOUCHER( COMPLAIN_ID, MSISDN, VISIBLE_CARD_NUMBER, CARD_SL, COMPLAIN_STATUS, REMARKS, CREATED_AT)
# VALUES ('2622345','01860748020','222','44424','1',NULL,SYSDATE)""" db.executeQuery(Query=sql)

# try: dsn_tns = cx_Oracle.makedsn('192.168.7.51', 1521, service_name='orcl') conn = cx_Oracle.connect(
# user='ROBI_RPA1', password='Robi55Robi#@!', dsn=dsn_tns) cursor = conn.cursor() sql = f"""INSERT INTO
# RPA_DIV_ERASE_VOUCHER( COMPLAIN_ID, MSISDN, VISIBLE_CARD_NUMBER, CARD_SL, COMPLAIN_STATUS, REMARKS, CREATED_AT)
# VALUES ('922345','01860748020','222','44424','1',NULL,SYSDATE)""" cursor.execute(sql) conn.commit() print('Insert
# Done')
#
# except Exception as e:
#     log.log_critical(f"There is a problem with Oracle DETAIL(single_data_record): EXCEPTION - {e}")
#     log.log_error(e)
#     print(e)

# try:
#     dsn_tns = cx_Oracle.makedsn('192.168.7.51', 1521, service_name='orcl')
#     conn = cx_Oracle.connect(user='ROBI_RPA1', password='Robi55Robi#@!', dsn=dsn_tns)
#     cursor = conn.cursor()
#     date = dt.date.today() - relativedelta(months=6)
#     print(date)
#     sql = f"SELECT * FROM RPA_DIV_ERASE_VOUCHER"
#     cursor.execute(sql)
#     res = cursor.fetchall()
#     print(res)
#     if not res:
#         cursor.close()
#         print('Query Excution Error')
#     else:
#         cursor.close()
#         print('Query Excution Successfully')
#         log.log_info("Data Fetch Successfully")
# except cx_Oracle.DatabaseError as e:
#     print('DB Connection/Query Exception')
#     log.log_critical("There is a problem with Oracle DETAILS : EXCEPTION - {e}")

db = database.DB()
download_path = db.get_download_path()
# print('Download = ', download_path)
pattern_file = "Sales Report"
found_file = 0
export_able_file = None
for filename in gb.glob(download_path + '/'+pattern_file+'*', recursive=False):
    export_able_file = filename
    found_file = 1
    if found_file == 1:
        break

if found_file == 1:
    print("File = ", export_able_file)
    # data_files = pd.ExcelFile(export_able_file)
    df = pd.read_excel(export_able_file)
    print(df)





# with open("../env_config.json") as config_file:
#     data = json.load(config_file)
#
# link = data['link']
# Key = data['PassPhase']
# EMAIL = CryptoPassPhase.decrypt(Key, data['email'])
# PASSWORD = CryptoPassPhase.decrypt(Key, data['password'])
#
# Credentials = pd.DataFrame(columns=["email", "password"], data=[[EMAIL, PASSWORD]])
# print(Credentials)
# driver = XMLWrapper()
# driver.automate_xml("../apps/xml/crmlogin.xml", df=Credentials)
#
# time.sleep(1)
#
# driver.automate_xml("../apps/xml/exportfilter.xml", df=Credentials)
