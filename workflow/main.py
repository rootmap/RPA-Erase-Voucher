import json
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from datetime import datetime
import time
import os
import glob as gb
from dateutil.relativedelta import relativedelta
from selenium.common.exceptions import TimeoutException

from apps.encryption import CryptoPassPhase
from pages.pages_xml_wrapper import XMLWrapper
from apps.database import DB
from apps.helper import Helper
from apps.api_helper import RPAApi
from apps.config import ConfigParser
from apps.app_utils import AppUtils

crm_api_object = RPAApi()
xml_wrapper_object = XMLWrapper()
db_object = DB()
conf = ConfigParser()

# print("Calling SMS API")
# crm_api_object.smsapi(msg="Test SMS for RPA", msisdn="01677136045")
# crm_api_object.stop_execution()

helper = Helper(webpage=xml_wrapper_object.webpage, driver=xml_wrapper_object.webpage.driver)
credentials = conf.get_credentials()
AppUtils.rpa_running_flag(flag="Start")
compile_data = []
try:
    helper.log_info(msg="Running Wrapper Main....")
    print("Running Wrapper Main....")
    compile_data = helper.run_wrapper(wrapper=xml_wrapper_object, wrapper_df=credentials)
except TimeoutException as element_not_found:
    helper.log_info(msg="No SR found")
    print("No SR Found.")
    xml_wrapper_object.webpage.end()


row_id = 1
total_compile_data = len(compile_data)
if total_compile_data > 0:
    for grid_row in compile_data:
        smart_script_list = helper.read_smart_script_and_validate_sr(grid_row=grid_row, row_id=row_id,
                                                                     compile_total=total_compile_data,
                                                                     wrapper=xml_wrapper_object, api=crm_api_object)
        print(smart_script_list)
        # exit(1)
        if smart_script_list['ERROR'] == 'Smart Script Not Found':
            api_status = "Failed"
            api_msg = smart_script_list['ERROR']
        else:
            api_status, api_msg = helper.recharge_erashed_voucher(smart_script=smart_script_list, api=crm_api_object)
            api_status, api_msg = helper.update_sr_status(smart_script=smart_script_list, api=crm_api_object,
                                                      status=api_status, message=api_msg)
            helper.insert_erase_voucher_db_log(db=db_object, smart_script=smart_script_list, status=api_status,
                                           message=api_msg)
        row_id = row_id + 1

    for grid_row in compile_data:
        print(grid_row)
print("Closing Browser JOB")
xml_wrapper_object.webpage.end()
