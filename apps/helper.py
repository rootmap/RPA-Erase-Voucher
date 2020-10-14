import json
import sys
from datetime import datetime
import time
import traceback
import pandas as pd
from apps.encryption import CryptoPassPhase
from functools import wraps
from utils.logger import Logger
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from apps.app_utils import AppUtils


#   log = Logger.get_instance()

def retry(delay=10, retries=4):
    def retry_decorator(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            opt_dict = {'retries': retries, 'delay': delay}
            while opt_dict['retries'] > 1:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    msg = "Exception: {}, Retrying in {} seconds...".format(e, delay)
                    print(msg)
                    time.sleep(opt_dict['delay'])
                    opt_dict['retries'] -= 1
            return f(*args, **kwargs)

        return f_retry

    return retry_decorator


def wait(func):
    def wrapper(instance, *args, **kwargs):
        try:
            func(instance, *args, **kwargs)
        except NoSuchElementException as exception:
            try:
                element_present = instance.get_element_presence(*args, **kwargs)
                WebDriverWait(instance.driver, instance.timeout).until(element_present)
                print(traceback.format_exc())
                func(instance, *args, **kwargs)
            except TimeoutException as timeoutexception:
                print("Element not found Details : {0} - {1} - {2}".format(func.__name__, args, kwargs))
                print(timeoutexception)
                print(traceback.format_exc())
                raise timeoutexception

    return wrapper


class Helper:
    def __init__(self, webpage, driver):
        self.webpage = webpage
        self.driver = driver
        self.log = Logger.get_instance()
        self.log.log_warn(type(self.webpage))

    def stop_execution(self):
        print('Stopping Execution')
        self.webpage.end()
        self.log_info(msg="Execution Stopped")
        sys.exit('Stopping Execution')

    def escape_unavailability(self, push_keys, data_type="count"):
        push_key = push_keys
        for i in range(1, 3):
            print("Initiating loop TryCatch = " + str(i))
            self.log_info(msg="Initiating loop TryCatch = " + str(i))
            push_key_action = push_key
            if data_type == "count":
                if int(push_key_action) > 0:
                    print("got beak for " + str(push_key_action))
                    break
                else:
                    push_key
            else:
                if str(push_key_action) > 5:
                    print("got beak for " + str(push_key_action))
                    break
                else:
                    push_key

        return push_key

    def primary_data_initiate_smart_script(self, pull_primary_data):

        element_check = self.check_table_record(output_data="data")
        self.log_info(msg="Getting CRM Open Complain List = " + str(element_check))
        pull_primary_data = self.pull_primary_data(element_check=element_check)
        self.log_info(msg="Push CRM Complain list to an list = " + str(element_check))
        self.click_first_complain()
        self.click_smart_screen_menu()
        self.choosing_smart_screen_item()
        return pull_primary_data

    def initiate_smart_script_data(self, pull_primary_data, index=0):
        smart_script_table_rows_total = self.check_table_record(output_data="count")
        self.log_info(msg="Getting CRM " + str(index) + " Index Complain Smart Script Data = " + str(
            smart_script_table_rows_total))
        if smart_script_table_rows_total > 1:
            smart_script_table_rows = self.check_table_record(output_data="data")
            self.log_info(msg="Index " + str(index) + " Smart Script Data = " + str(smart_script_table_rows))
            pull_primary_data = self.push_smart_script_data_to_data_grid(index_key=index,
                                                                         primary_data=pull_primary_data,
                                                                         smart_script_element_check=smart_script_table_rows)
            self.log_info(msg="Index " + str(index) + " Smart Script Data push into Main Data Grid = " + str(
                smart_script_table_rows))
        else:
            self.log_info(msg="No Smart Script Found for " + str(index) + " complain list.")

        return pull_primary_data

    def push_more_smart_script_data(self, pull_primary_data):
        self.log_info(
            msg="Checking Length main data grid for getting other smart script data = " + str(len(pull_primary_data)))
        if len(pull_primary_data) > 1:
            self.log_info(msg="Got max length to execute other smart script = " + str(len(pull_primary_data)))
            for i in range(1, len(pull_primary_data)):
                print("Loop for SMart Scrip " + str(i))
                self.clicking_crm_data_info_slide()
                time.sleep(3)
                pull_primary_data = self.initiate_smart_script_data(pull_primary_data=pull_primary_data, index=i)
        else:
            self.log_info(msg="Data Grid Data Length Not Match to Generate Other Smart Script = ")

        return pull_primary_data

    def log_info(self, msg):
        return self.log.log_info(msg)

    def log_critical(self, msg):
        return self.log.log_critical(msg)

    @retry(1, 5)
    def crm_table_rows(self, locator, read_col=''):
        table_rows = 0
        data_row = []
        for row in self.webpage.get_elements(locator=locator, locator_type="css"):
            if read_col != '':
                col = []
                for td in row.find_elements_by_css_selector(read_col):
                    col.append(td.text)
                data_row.append(col)
            else:
                table_rows = table_rows + 1
        if read_col != '':
            return data_row
        else:
            return table_rows

    def check_table_record(self, output_data="count"):
        record_table_available = 0
        try:
            time.sleep(3)
            if output_data == "count":
                element_check = self.crm_table_rows(locator="#s_2_l tbody tr")
                record_table_available = int(element_check) - 1
                self.log.log_info("Count Table Record Found = " + str(record_table_available))
            else:
                element_check = self.crm_table_rows(locator="#s_2_l tbody tr", read_col='td')
                record_table_available = element_check
                self.log.log_info("Table Data Record Found = " + str(record_table_available))
        except NoSuchElementException:
            self.log.log_critical("Table Not Exists ")
            #   print('Table Exists = ', 'Data Not Available')
        #   print('Table Record = ', record_table_available)
        return record_table_available

    @wait
    def set_text(self, locator, locator_type="xpath", param_str=''):
        #   print("Clicking Locator = ", locator)
        #   return self.webpage.get_element(locator=locator, locator_type=locator_type).click()
        element = self.webpage.get_elements(locator=locator, locator_type=locator_type)
        element.sendKeys(param_str)

    @wait
    def click(self, locator, locator_type="xpath"):
        #   print("Clicking Locator = ", locator)
        #   return self.webpage.get_element(locator=locator, locator_type=locator_type).click()
        return self.webpage.click(locator=locator, locator_type=locator_type)

    @retry(1, 5)
    def click_first_complain(self):
        locator = '//*[@id="1SR_Number"]/a'
        self.log.log_info("Clicking First Complain Row")
        return self.click(locator=locator)

    def click_smart_screen_menu(self):
        locator = '#s_vctrl_div_tabScreen'
        locator_type = "css"
        self.log.log_info("Clicking First Complain Smart Script Menu")
        return self.click(locator=locator, locator_type=locator_type)

    def choosing_smart_screen_item(self):
        locator = '//a[text()="Smart Script"]'
        self.log.log_info("Clicking First Complain Smart Script Menu Item")
        return self.click(locator=locator)

    # def clicking_crm_data_info_slide(self):
    #     locator = '//*[@id="s_4_1_169_0"]'
    #     self.log.log_info("Clicking Slide Top Data Switch Menu")
    #     return self.click(locator=locator)

    def pull_primary_data(self, element_check=None):
        if element_check is None:
            element_check = []
        pull_primary_data = []
        for row in element_check:
            if row[2] != "":
                row_col = [row[2], row[3], row[4]]
                pull_primary_data.append(row_col)
            else:
                self.log.log_critical("Failed to load primary data array from CRM ")
        #   print('pull_primary_data = ', pull_primary_data)
        self.log.log_info("Pull Primary Data = " + str(pull_primary_data))
        return pull_primary_data

    def push_smart_script_data_to_data_grid(self, index_key=0, primary_data=[], smart_script_element_check=[]):
        if len(smart_script_element_check) > 0:
            for td_row in smart_script_element_check:
                if td_row[1] != "":
                    primary_data[index_key].append(td_row[2])
            self.log.log_info(
                "Smart Script length " + str(len(smart_script_element_check)) + " And Push To Pull Data Array")
            return primary_data
        else:
            #   print("Smart Script Data ({index_key})", index_key)
            self.log.log_critical(
                "Smart Script length " + str(len(smart_script_element_check)) + " And Push To Pull Data Array")
            return primary_data

    def run_wrapper(self, wrapper, wrapper_df):
        wrapper_xml_link = AppUtils.conf['xml_wrapper_path']
        wrapper.automate_xml(location=wrapper_xml_link, df=wrapper_df)
        self.log_info(msg="Automate XML Run Complete")
        time.sleep(3)
        print("Checking Download Directory for Downloaded Files")
        file_name = AppUtils.new_file_name()
        file_moved = AppUtils.move_downloaded_file(file_name=file_name)
        self.log_info(msg="File Download And Moved = " + str(file_moved))
        time.sleep(3)
        download_file_location = AppUtils.conf['crm_download_file_directory']
        df = pd.read_csv(r""+download_file_location+"\\" + file_moved,
                         sep="\t",
                         header=None,
                         index_col=[0, 1, 2, 3],
                         encoding='utf-16le')
        print(df)
        compile_data = []
        for rows in df.iterrows():
            print(rows[0][1])
            if rows[0][1] != "SR #":
                row = [rows[0][1], rows[0][2], rows[0][3]]
                compile_data.append(row)

        print(compile_data)
        return compile_data

    def read_smart_script_and_validate_sr(self, grid_row, row_id, compile_total, wrapper, api):
        sr_id = grid_row[0]
        msisdn = grid_row[1]
        complain_ids = pd.DataFrame(
            columns=[
                "sr_id",
                "msisdn",
                "sr_name"
            ],
            data=[
                [
                    sr_id,
                    msisdn,
                    grid_row[2]
                ]
            ]
        )
        counter_log = str(row_id) + " Out of " + str(compile_total)
        # row_id = row_id + 1
        grid_row.append(counter_log)

        print("Initiating SR#ID [" + grid_row[0] + "] Second Search XML")
        wrapper_find_smart_script = AppUtils.conf['xml_wrapper_smart_script_path']
        wrapper.automate_xml(location=wrapper_find_smart_script,
                             df=complain_ids)
        time.sleep(3)
        smart_script_list = {'SR_ID': sr_id, 'RECHARGE_UNIQUE_SERIAL': 'DSAW345', 'MSISDN': msisdn, 'SERIAL_NUMBER': '',
                             'DENOMINATION': 0, 'VISIBLE_SECRET_DIGIT': '', 'ERROR': '', 'COUNTER_LOG': counter_log}
        total_row_in_smart_script = self.check_table_record(output_data="count")
        if total_row_in_smart_script > 0:
            print("SR#ID [" + str(grid_row[0]) + "] : Total Record = " + str(total_row_in_smart_script))
            smart_script = self.check_table_record(output_data="data")
            for ss_row in smart_script:
                if ss_row[1] != "":
                    grid_row.append(ss_row[2])
                    if ss_row[1].rstrip().lstrip() == "Serial Number":
                        smart_script_list['SERIAL_NUMBER'] = ss_row[2]
                    elif ss_row[1].rstrip().lstrip() == "Denomination":
                        smart_script_list['DENOMINATION'] = ss_row[2]
                    elif ss_row[1].rstrip().lstrip() == "Visible secret digits":
                        smart_script_list['VISIBLE_SECRET_DIGIT'] = ss_row[2]
                    print("SR#ID [" + str(grid_row[0]) + "] = Smart Script [ Field Name : " + str(
                        ss_row[1]) + " Value :" + str(ss_row[2]) + "]")
                    # in progress moved to other place.
        else:
            print("SR#ID [" + str(grid_row[0]) + "] : No Record Found")
            smart_script_list['ERROR'] = "Smart Script Not Found"
        return smart_script_list

    def recharge_erashed_voucher(self, smart_script, api):
        missdn = api.mob_num_to_10_digit(smart_script['MSISDN'])
        print(f"Request from cbs_damage_card_recharge Send to clear blacklist msisdn: {missdn}")
        api_clear_blacklist = None
        i = 1
        while i < 3:
            time.sleep(1)
            api_clear_blacklist = api.cbs_remove_msisdn_blacklist(msisdn=missdn)
            if api_clear_blacklist:
                break
            i += 1

        i = 1
        api_response = None
        while i < 3:
            time.sleep(1)
            api_response = api.cbs_damage_card_recharge(msisdn=smart_script['MSISDN'],
                                                        card_serial=smart_script['SERIAL_NUMBER'],
                                                        pin_no=smart_script['VISIBLE_SECRET_DIGIT'])
            if api_response:
                break
            i += 1

        if api_response is not None:
            json_content = json.loads(api_response.content)
            response_list = json_content['soapenv:Envelope']['soapenv:Body']['ars:RechargeResultMsg']['ResultHeader']
            api_response = response_list

        self.log_info(msg="API Response  = " + str(api_response))
        print('API Response :', api_response)

        api_status_validate = "Failed"
        api_status_msg = "Unable to get response!"
        try:
            if api_response['cbs:ResultDesc']:
                api_status_msg = api_response['cbs:ResultDesc']
                api_status_code = api_response['cbs:ResultCode']

                if api_status_code == 0:
                    api_status_msg = api_status_msg
                    api_status_validate = "Successful"
        except Exception as e:
            api_status_validate = "Failed"
            api_status_msg = "Unable to get response!"

        return api_status_validate, api_status_msg

    def update_sr_status(self, smart_script, api, status, message):
        print("Got Final Status ", status, message)
        self.log_info(msg="CBS Response For CRM = " + str(status) + " , " + str(message))
        if status == 'Successful':
            api.crm_complain_update_counter(smart_script['MSISDN'], smart_script['SR_ID'], current_status="Open",
                                            target_status="In Progress",
                                            error=message)
            time.sleep(2)
            api.crm_complain_update_counter(smart_script['MSISDN'], smart_script['SR_ID'],
                                            target_status="Completed",
                                            current_status="In Progress",
                                            error=message)
            time.sleep(2)
            api.crm_complain_update_counter(smart_script['MSISDN'], smart_script['SR_ID'],
                                            target_status="Close",
                                            current_status="Completed",
                                            error=message)
            print('Executing CRM SRID [Closed] : ', smart_script['MSISDN'], smart_script['SR_ID'], message)
        else:
            time.sleep(2)
            api.crm_complain_update_counter(smart_script['MSISDN'], smart_script['SR_ID'],
                                            target_status="Cancelled",
                                            current_status="Open",
                                            error=message)
            api.smsapi(msg="Dear Customer, We are unable to process your request.", msisdn=smart_script['MSISDN'])
            print('Executing CRM SRID [Completed] : ', smart_script['MSISDN'], smart_script['SR_ID'],
                  message)

        return status, message

    def insert_erase_voucher_db_log(self, db, smart_script, status, message):
        self.log_info(msg="API Response for DB  = " + str(status) + " , " + str(message))
        insert_db_query = r"Insert INTO CRM_DV_ERASE_VOUCHER (SR_NUMBER, MSISDN, COUNTER_LOG, "
        insert_db_query = insert_db_query + r"SERIAL_NUMBER, DENOMINATION, VISIBLE_SECRET_DIGIT, "
        insert_db_query = insert_db_query + r"API_VALIDATION, ERROR) VALUES "
        insert_db_query = insert_db_query + r"('" + str(smart_script['SR_ID']) + "','" + str(
            smart_script['MSISDN']) + "','" + str(smart_script['COUNTER_LOG']) + "',"
        insert_db_query = insert_db_query + r"'" + str(smart_script['SERIAL_NUMBER']) + "',"
        insert_db_query = insert_db_query + r"'" + str(smart_script['DENOMINATION']) + "',"
        insert_db_query = insert_db_query + r"'" + str(smart_script['VISIBLE_SECRET_DIGIT']) + "',"
        insert_db_query = insert_db_query + r"'" + str(status) + "',"
        insert_db_query = insert_db_query + r"'" + str(message) + "')"
        print(insert_db_query)
        ins_status = db.execute_query(insert_db_query)
        print("Closing Ticket")
        self.log_info(msg="Closing Ticket ")
        return ins_status
