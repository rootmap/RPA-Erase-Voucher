# Region: Imports

import pandas as pd
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException

from apps.api_and_database2 import DB
from apps.crm2 import RpaCRM
from apps.service_validation import APIValidation, DataValidation
from utils.custom_exception import ExpectedDataNotFoundException, NoneResponseException
from utils.logger import Logger

# Region: Initialization Static
log = Logger.get_instance()
log.log_start()
apivalid = APIValidation()
datav = DataValidation()
db = DB()
username = 'rpa'
password = 'Windows@10'
# link = 'https://10.101.26.30/ecommunications_enu/start.swe?SWECmd=Login&SWECM=S&SRN=&SWEHo=10.101.26.30'
brows = 'chrome'
# link = 'https://c1.robi.com.bd/ecommunications_enu/start.swe?SWECmd=GotoView&SWEView=CUT+Home+Page+View+(CME)&SWERF=1&SWEHo=c1.robi.com.bd&SWEBU=1'
# link = 'https://c1.robi.com.bd/ecommunications_enu/start.swe?SWECmd=GotoView&SWEView=Service+Request+Screen+Homepage+View&SWERF=1&SWEHo=c1.robi.com.bd&SWEBU=1'
link = 'https://c1.robi.com.bd/ecommunications_enu/start.swe?SWECmd=GotoView&SWEView=Service+Request+Screen+Homepage+View&SWERF=1&SWEHo=c1.robi.com.bd&SWEBU=1'
# End Region

# Region: Data Frame
df_rebate_fail = pd.DataFrame(
    columns=['SR_NUMBER', 'MSISDN', 'PACK', 'PACK_ID', 'BONUS_PACK', 'BONUS_PACK_ID', 'PRICE', 'USAGE', 'DB_VALIDATION',
             'ERROR'])
# End Region

crm = RpaCRM(brows, link)
crm.login(username, password)
crm.filter()
crm.csv_download()
complain_list_file = crm.check_file('output.txt')

if not complain_list_file:
    log.log_warn("No new Complain Found File Closing RPA")
    exit(1)

# complain_list = pd.read_csv("C:/Users/rashid.rayhan/Downloads/output.txt", encoding='utf-16')
complain_list = pd.read_csv("C:/Users/crm_rpa/Downloads/output.txt", encoding='utf-16')
complain_list = complain_list.sort_values(by='Log Date')

log.log_debug(complain_list)
# crm.pages.end()
# crm = None
counter = 0
error = None
for row in range(len(complain_list.index)):
    counter = counter + 1
    msisdn = complain_list.iat[row, 2]
    msisdn = str(msisdn)
    sr_id = complain_list.iat[row, 1]

    # # for testing
    # sr_id = "20011527297755876"
    # msisdn = "8801644577488"

    counter_log = f"{counter} out of {len(complain_list.index)}"
    log.log_info(f"\n\n\n{counter_log}. SR: {sr_id}, MSISDN: {msisdn}")
    print(f"\n\n\n{counter_log}. SR: {sr_id}, MSISDN: {msisdn}")

    log.log_info(f"\n\nExsistance Check")
    print(f"\n\nExsistance Check")

    row = db.check_sr_exsitance(MSISDN=msisdn, SR_NUMBER=sr_id)
    if row is None or row > 0:
        if row is None:
            log.log_warn(f"Unable to find databse response for SR_ID : {sr_id}")
            print(f"Unable to find databse response for SR_ID : {sr_id}")
        if row > 0:
            log.log_warn(f"This complain handled before SR_ID : {sr_id}")
            print(f"This complain handled before SR_ID : {sr_id}")
        continue

    # Prepaid PostPaid Check
    log.log_info(f"\n\nPrepaid Postpaid Check")
    print(f"\n\nPrepaid Postpaid Check")
    try:
        response = apivalid.pre_porst_check(msisdn=msisdn)
        print(response)
    except ExpectedDataNotFoundException as e:
        error = f"Unable to Process as provided phone number is Postpaid."
        log.log_warn(error)
        print(error)
        db.single_data_record(SR_NUMBER=sr_id, MSISDN=msisdn,
                              ERROR=error, COUNTER_LOG=counter_log, LIST_TYPE="black")
        continue
    except NoneResponseException as e:
        error = "Unable to Find number catagory for Prepaid/Postpaid Therefore not processing"
        log.log_critical(error)
        db.single_data_record(SR_NUMBER=sr_id, MSISDN=msisdn,
                              ERROR=error, COUNTER_LOG=counter_log, LIST_TYPE="black")
        continue

    # History validation
    log.log_info(f"\n\nHistory validation Check")
    print(f"\n\nHistory validation Check")
    try:
        db_check = datav.history_validation(msisdn=msisdn, sr_id=sr_id)
    except ExpectedDataNotFoundException as e:
        error = "The Complain by the MSISDN Existed Previously with in 6 months"
        log.log_critical(f"{error}")
        print(error)
        db.single_data_record(SR_NUMBER=sr_id, MSISDN=msisdn, USAGE=None, PACK_ID=None, BONUS_PACK=None,
                              DB_VALIDATION='0', PRICE=None, ERROR=error, COUNTER_LOG=counter_log, LIST_TYPE="black")
        apivalid.crm_complain_update_counter(msisdn=msisdn, sr_id=sr_id, current_status="Open",
                                             target_status="Cancelled", error=error)

        msg = "Dear Customer, we are unable to adjust the requested amount."
        apivalid.smsapi(msisdn=msisdn, msg=msg)
        continue

    # Download Smart Script
    log.log_info(f"\n\nDownload Smart Script")
    print(f"\n\nDownload Smart Script")
    try:
        crm_smart_script = RpaCRM(brows, link)
        crm_smart_script.login(username, password)
    except Exception as e:
        log.log_warn(f"Login Exception - {e}")
        continue

    try:
        crm_smart_script.data_pack_details(sr_id)
    except ExpectedDataNotFoundException as e:
        error = "Smart Script Download failed"
        log.log_error(e)
        continue
    except (NoSuchElementException, TimeoutException) as e:
        error = "No Smart Script Found"
        log.log_error(e)
        log.log_error(e.args)
        log.log_warn(f"Probably No Smart Script Found here Details : MSISDN - {msisdn} SR_ID - {sr_id}")
        print(error)
        counter_log = f"{counter} out of {len(complain_list.index)}"
        db.single_data_record(SR_NUMBER=sr_id, MSISDN=msisdn,
                              ERROR=error, COUNTER_LOG=counter_log, LIST_TYPE="black")
        complain_status_response = apivalid.crm_complain_update_counter(msisdn=msisdn, sr_id=sr_id,
                                                                        current_status="Open",
                                                                        target_status="Cancelled", error=error)
        continue
    except WebDriverException as e:
        log.log_error(e)
        print(e)
        continue

    # Check Smart Script
    data_info_file = crm_smart_script.check_file('output (1).txt')
    if not data_info_file:
        log.log_warn(f"No Smart Script Found Details : SR_ID - {sr_id} MSISDN - {msisdn}")
        continue

    #GET Smart Script Data
    log.log_info(f"\n\nGET Smart Script Data")
    print(f"\n\nGET Smart Script Data")
    try:
        smart_script_info = datav.smart_scripts_info()
        trade_time = smart_script_info.get("trade_time")
        pack = smart_script_info.get("pack")
        bonus_pack = smart_script_info.get("bonus_pack")
        print(smart_script_info)
        log.log_info(f"smart_script_info: {smart_script_info}")
    except Exception as e:
        error = "Get Smart Script data Exception"
        log.log_critical(f"smart_script_info exception - {e}")
        print(error)
        continue

    # Get Pack Price
    log.log_info(f"\n\nGET Price")
    print(f"\n\nGET Price")
    try:
        pack_price = apivalid.get_price(msisdn, trade_time)
        log.log_info(f"Pack Price: {pack_price}")
        print(f"Pack Price: {pack_price}")
    except ExpectedDataNotFoundException as e:
        error = f"GET PRICE FAILED, Trade Time - {trade_time}"
        log.log_critical(error)
        print(error)
        db.single_data_record(SR_NUMBER=sr_id, MSISDN=msisdn, ERROR=error, COUNTER_LOG=counter_log, PACK=pack,
                              BONUS_PACK=bonus_pack, LIST_TYPE="black")
        apivalid.crm_complain_update_counter(msisdn, sr_id, current_status="Open", target_status="Cancelled",
                                             error=error)
        continue

    # Get Pack Details
    log.log_info(f"\n\nGET Pack Details")
    print(f"\n\nGET Pack Details")
    try:
        pack_details = apivalid.find_pack_id(msisdn=msisdn, pack=pack, bonus_pack=bonus_pack)
        print(pack_details)
        pack_found = pack_details.get("pack_found")
        pack_id = pack_details.get("pack_id")
        plan_usage = pack_details.get("plan_usage")
        bonus_pack_found = pack_details.get("bonus_pack_found")
        bonus_pack_id = pack_details.get("bonus_pack_id")

        plan_usage = str(plan_usage)
        print(plan_usage, type)

        if plan_usage != "0":
            error = "pack has been used"
            db.single_data_record(SR_NUMBER=sr_id, MSISDN=msisdn,
                                  USAGE=plan_usage, PACK_ID=pack_id, PACK=pack, BONUS_PACK=bonus_pack,
                                  ERROR=error, COUNTER_LOG=counter_log, LIST_TYPE="black")
            log.log_info(
                f"Unable to Process for the following complain - {sr_id}  MSISDN - {msisdn} ERROR - {error}")
            msg = "Dear Customer, we are unable to adjust the requested amount."
            apivalid.smsapi(msisdn=msisdn, msg=msg)
            apivalid.crm_complain_update_counter(msisdn, sr_id, current_status="Open", target_status="Cancelled",
                                                 error=error)
            continue

    except ExpectedDataNotFoundException as e:
        error = "Unable to find pack from customer pack list"
        db.single_data_record(SR_NUMBER=sr_id, MSISDN=msisdn, PACK=pack,
                              BONUS_PACK=bonus_pack,
                              ERROR=error, COUNTER_LOG=counter_log, LIST_TYPE="black")
        log.log_info(f"Unable to Process for the following complain - {sr_id}  MSISDN - {msisdn} ERROR - {error}")
        print(error)
        apivalid.crm_complain_update_counter(msisdn, sr_id, current_status="Open", target_status="Cancelled",
                                             error=error)
        continue

    log.log_info(f"\n\n Terminate Pack")
    print(f"\n\nTerminate Pack")
    pack_terminate = False
    try:
        apivalid.terminate_pack(msisdn, pack_id)
        pack_terminate = True
        print("pack_terminated")
    except ExpectedDataNotFoundException as e:
        error = f"Pack Termination Fail."
        log.log_critical(f"{error}, Pack Terminate EXCEPTION - {e}")
        print(error)
        db.single_data_record(SR_NUMBER=sr_id, MSISDN=msisdn, PACK=pack, USAGE=plan_usage,
                              PACK_ID=pack_id, BONUS_PACK=bonus_pack, BONUS_PACK_ID=bonus_pack_id,
                              DB_VALIDATION=db_check, PRICE=pack_price,
                              COUNTER_LOG=counter_log, ERROR=error,
                              LIST_TYPE="Off_White")

        df_rebate_fail = df_rebate_fail.append(
            other={'SR_NUMBER': sr_id, 'MSISDN': msisdn,
                   'PACK': pack, 'USAGE': None,
                   'PACK_ID': None, 'BONUS': bonus_pack,
                   'BONUS_PACK_ID': None, 'DB_VALIDATION': None,
                   'PRICE': pack_price, 'ERROR': "Pack Terminate Fail"},
            ignore_index=True)
        pass

    # terminate Bonus PACK
    if bonus_pack_found and pack_terminate:
        log.log_info(f"\n\n Terminate Bonus Pack")
        print(f"\n\nTerminate Bonus Pack")
        try:
            apivalid.terminate_pack(msisdn, bonus_pack_id)
        except ExpectedDataNotFoundException as e:
            log.log_critical(f"Bonus Pack Terminate EXCEPTION - {e}")
            print("bonus pack terminate fail")
            pass

    # Rebate
    rebate_flag = False
    if pack_terminate:
        log.log_info(f"\n\n Rebate, Amount: {pack_price}")
        print(f"\n\nRebate, Amount: {pack_price}")

        try:
            rebate_flag = apivalid.rebate(msisdn, pack_price)

            db.single_data_record(SR_NUMBER=sr_id, MSISDN=msisdn, PACK=pack, USAGE=plan_usage,
                                  PACK_ID=pack_id, BONUS_PACK=bonus_pack, BONUS_PACK_ID=bonus_pack_id,
                                  DB_VALIDATION=db_check, PRICE=pack_price,
                                  COUNTER_LOG=counter_log, LIST_TYPE="white")

            msg = "Dear Customer, Your requested amount has been adjusted. To check your account balance, please dial *1#. Thank you. "
            apivalid.smsapi(msisdn, msg)
            error = "Operation successful"

        except ExpectedDataNotFoundException as e:
            error = "Rebate Fail"
            log.log_critical(f"Rebate EXCEPTION - {e}")
            print(error)

            df_rebate_fail = df_rebate_fail.append(
                other={'SR_NUMBER': sr_id, 'MSISDN': msisdn,
                       'PACK': pack, 'USAGE': None,
                       'PACK_ID': None, 'BONUS': bonus_pack,
                       'BONUS_PACK_ID': None, 'DB_VALIDATION': None,
                       'PRICE': pack_price, 'ERROR': error},
                ignore_index=True)
            db.single_data_record(SR_NUMBER=sr_id, MSISDN=msisdn, PACK=pack, USAGE=plan_usage,
                                  PACK_ID=pack_id, BONUS_PACK=bonus_pack, BONUS_PACK_ID=bonus_pack_id,
                                  DB_VALIDATION=db_check, PRICE=pack_price,
                                  COUNTER_LOG=counter_log, ERROR=error,
                                  LIST_TYPE="Off_White")

    complain_update_response = apivalid.crm_complain_update_counter(msisdn, sr_id, current_status="Open",
                                                                    target_status="In Progress", error=error)
    if complain_update_response != "Success":
        continue
    complain_update_response = apivalid.crm_complain_update_counter(msisdn, sr_id, current_status="In Progress",
                                                                    target_status="Completed", error=error)
    if complain_update_response != "Success":
        continue
    apivalid.crm_complain_update_counter(msisdn, sr_id, current_status="Completed", target_status="Closed", error=error)

apivalid.smsapi('8801833182430', 'All done')
df_rebate_fail.to_csv("C:/Users/crm_rpa/Downloads/rebate_fail_list.csv", index=False, mode='a', header=False)
log.log_end()
