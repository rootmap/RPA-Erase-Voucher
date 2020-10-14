import json
from datetime import datetime
import sys
import uuid
import requests
import time
#   from utils.custom_exception import IllegalArgumentError
from utils.logger import Logger
from xml.etree import ElementTree


class RPAApi:
    token = None
    token_genarate_url = None
    postpaid_recharge_url = None
    prepaid_recharge_url = None
    user_name = None
    password = None
    authorization_token = None
    adjust_balance_url = None
    sms_url = None

    def __init__(self):
        self.log = Logger.get_instance()
        self.user_name = "IT_RPA_AppS"
        self.password = "RoboTIC%24HerO)24"
        self.authorization_token = "UHpTdjBGc1RkRUQ3VXB4dmNMX3VWeXh4SG9BYTpqaW1xN0RTTkxzdkZpQlJaN0Q0Vjd1Z0xGQ0Fh"
        self.token_genarate_url = 'https://apigate.robi.com.bd/token'
        self.cbs_damage_card_recharge_url = 'https://apigate.robi.com.bd/cbs/cbsDamageCardRecharge/v1/somapi/postpaid/voucherRecharge'
        self.cbs_blacklist_remove_url = 'https://apigate.robi.com.bd/cbs/cbsBlacklisting/v1/somapi/postpaid/blacklist/msisdn'
        self.sms_url = "http://10.101.11.164:8888/cgi-bin/sendsms"
        self.token = self.access_token()

    def stop_execution(self):
        print('Stopping Execution')
        self.log.log_info(msg="Execution Stopped")
        sys.exit('Stopping Execution')

    def access_token(self):
        url = self.token_genarate_url
        payload = "grant_type=password&username=" + self.user_name + "&password=" + self.password + "&scope=PRODUCTION"
        headers = {
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': "Basic " + self.authorization_token,
            'cache-control': "no-cache",
        }
        try:
            response = requests.post(url=url, data=payload, headers=headers, timeout=3)
            self.log.log_info(msg="Response received from MIFE")
            print(response.text)
            print(response.headers['Content-Type'])
            if response.headers['Content-Type'] == 'application/json; charset=UTF-8':
                return response.json()['access_token']
            else:
                return self.access_token()

        except requests.exceptions.RequestException as e:
            self.log.log_critical(msg="Unable to connect to apigate.robi.com.bd{e}")

    def mob_num_to_10_digit(self, mob=''):
        self.log.log_info(f"Converting MSISDN 10 For : {mob}")
        misdo_response = 0
        if len(mob) == 13 and mob.startswith('880'):
            misdo_response = mob[3:]
        elif len(mob) == 10 and mob.startswith('1'):
            misdo_response = mob
        elif len(mob) == 11 and mob.startswith('01'):
            misdo_response = mob[1:]

        return misdo_response

    def msisdn_to_13_digit(self, msisdn):
        msisdn = str(msisdn)
        if len(msisdn) == 13 and msisdn.startswith('880'):
            return msisdn
        elif len(msisdn) == 10 and msisdn.startswith('1'):
            return '880' + msisdn
        elif len(msisdn) == 11 and msisdn.startswith('01'):
            return '88' + msisdn
        else:
            self.log.log_warn(f"RPA Something wrong with the msisdn Details: MSISDN - {msisdn} TYPE - {type(msisdn)}")
            raise IllegalArgumentError

    def smsapi(self, msisdn, msg):
        msisdn = self.msisdn_to_13_digit(msisdn)
        url = self.sms_url
        querystring = {"user": "tester", "pass": "foobar", "to": msisdn, "text": msg, "from": "8123"}
        try:
            response = requests.get(url=url, params=querystring, timeout=3)
            if response.status_code == 200:
                self.log.log_info(
                    f"Response received from SMS KENEL Detail : MSISND - {msisdn} MSG - {msg}")
            else:
                self.log.log_critical(
                    f"Failed Response received from SMS KENEL Detail : MSISND - {msisdn} MSG - {msg} RESPONSE - {response.text}")
            self.log.log_info(f"SMS API Response for msisdn = {msisdn}, messege = {msg}, RESPONSE - {response.text}")
        except requests.exceptions.RequestException as e:
            self.log.log_critical(
                f"Unable to connect to SMS KENEL GATE WAY Details : For MSISDN - {msisdn} MESSAGE - {msg} EXCEPTION - {e}")

    def cbs_remove_msisdn_blacklist(self, msisdn):
        msisdn = self.mob_num_to_10_digit(mob=msisdn)
        self.log.log_info(f"Removing & CHecking Blacklist For : {msisdn}")
        cbs_response = {'responseCode': 1, 'responseDesc': 'Failed To Execute'}
        url = self.cbs_blacklist_remove_url+'/'+msisdn
        headers = {
                   'Content-Type': "application/json",
                   'cache-control': "no-cache",
                   'Authorization': "Bearer " + self.token
                  }
        try:
            response = requests.request("GET", url, headers=headers, timeout=3)
            self.log.log_info(f"Request Send to clear blacklist msisdn: {msisdn}")
            self.log.log_info(f"CBS unblock API response DETAILS : msisdn - {msisdn} response - {response}")
            print(f"Request Send to clear blacklist msisdn: {msisdn}")
            if response.status_code == 401:
                self.token = self.access_token()
                headers['Authorization'] = f'Bearer {self.token}'
                response = requests.request("GET", url, headers=headers, timeout=3)
            elif response.status_code == 500:
                return None
            elif response.status_code == 200:
                json_content = json.loads(response.content)
                print(json_content)
                return json_content
            else:
                return None
        except requests.exceptions.RequestException as e:
            self.log.log_error(e)
            return None

    def cbs_damage_card_recharge(self, msisdn, card_serial, pin_no):
        recharge_id = "ERASE" + datetime.now().strftime("%Y%m%d%H%M%S")
        print('TOKEN ID API = ', recharge_id)
        recharge_unique_serial = recharge_id
        missdn = self.mob_num_to_10_digit(msisdn)
        print('cbs_damage_card_recharge = MSISDN : ', missdn)
        card_serial = card_serial
        pin_no = pin_no
        i = 0
        id = recharge_id
        url = self.cbs_damage_card_recharge_url
        headers = {
            'Content-Type': "text/plain",
            'cache-control': "no-cache",
            'Authorization': "Bearer " + self.token,
            'Accept': "*/*"
        }

        payload = {
            'rechargeUniqueSerial': f"{recharge_unique_serial}",
            'missdn': f"{missdn}",
            'cardSerial': f"{card_serial}",
            'pinNo': f"{pin_no}"
        }

        print('payload', payload)

        headers = {'Content-Type': "application/json", 'cache-control': "no-cache",
                   'Authorization': "Bearer " + self.token, }

        try:
            response = requests.request("POST", url, data=json.dumps(payload), headers=headers, timeout=3)
            self.log.log_info(
                f"msisdn: {missdn}, try_count: {i}, ID: {id} -> Status code: {response.status_code}, Response Body: {response.text}")
            print(
                f"msisdn: {missdn}, try_count: {i}, ID: {id} -> Status code: {response.status_code}, Response Body: {response.text}")
            if response.status_code == 401:
                time.sleep(2)
                self.token = self.access_token()
                headers['Authorization'] = f'Bearer {self.token}'
                response = requests.request("POST", url, data=payload, headers=headers, timeout=3)
            elif response.status_code == 500:
                return None
            elif response.status_code == 200:
                print(response)
                return response
            else:
                return None
        except requests.exceptions.RequestException as e:
            self.log.log_error(e)
            self.log.log_error_msg(
                f"get price list failed, can't connect to apigate.robi.com.bd. SequenceID = {id} Error: {e}")
            print(f"Get Price Exception - {e}")
            return None

    def crm_complain_update(self, msisdn, sr_id, status, error=''):
        now = datetime.now()
        current_date_time = now.strftime("%Y-%m-%dT%H:%M:%S.0Z")
        id = "RPA_" + str(uuid.uuid4()) + "_" + datetime.now().strftime("%Y%m%d%H%M%S")

        reason = "Adjustment Given"
        root_cause = "Other"
        root_casue_detail = "Other"
        escalation = ""
        Solution = "Adjustment Given"
        if status == "Cancelled":
            reason = error
            root_cause = "Invalid Complaint"
            root_casue_detail = "Invalid Complaint"
            escalation = "Unable to Adjust the requested amount"
            Solution = "Adjustment Given"
        url = "http://lb_osb.robi.com.bd:7777/RobiAxiataSOA/RequesterABCS/ProxyServices/UpdateServiceRequest/2.0/UpdateServiceRequestReqABCSPS"
        payload = f"<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:upd=\"http://www.robi.com.bd/soa/xsd/UpdateServiceRequest/V2\" xmlns:com=\"http://www.robi.com.bd/soa/xsd/Common\">\n   <soapenv:Header/>\n   <soapenv:Body>\n      <upd:UpdateServiceRequest>\n         <upd:CommonComponents>\n            <com:IMSINum/>\n            <com:MSISDNNum/>\n            <com:ProcessingNumber>{id}</com:ProcessingNumber> <!--Mandatory Input:unique identifier to track the transaction-->\n            <com:RequestDateTime>{current_date_time}</com:RequestDateTime> <!--Conditional Mandatory: Holds the timestamp when the request came in. If it is being passed, it has to be in the exact format as mentioned. Else even the tag should also not be present. Empty tag will not be supported.-->\n            <com:SenderID>REM</com:SenderID> <!-- Mnadatory Input. Valid Values \"Remedy\" -->\n\t    <!--Optional: Holds the Source IP or Host Name of the application giving the request or the Service Invoker-->\n            <com:SourceHostName>xxxx</com:SourceHostName>\n         </upd:CommonComponents>\n         <upd:RequestType>UpdateServiceRequest</upd:RequestType> <!--Mandatory Input, valid value \"UpdateServiceRequest\" -->\n         <upd:Identification>\n            <upd:ServiceID>{msisdn}</upd:ServiceID> <!-- Mandatory: Holds  Subscriber MSISDN, this is sample value-->\n         </upd:Identification>\n         <upd:ServiceRequestDetails>\n            <upd:ServiceRequestSpecification>\n               \t<upd:ServiceReqNum>{sr_id}</upd:ServiceReqNum> <!-- Mandatory: Holds CRM SRNumber,  this is a sample Value -->\n               \t<upd:IncidentStatus>{status}</upd:IncidentStatus> <!-- Mandatory : Holds Status value. Valid values are ..\"Pending\" , \"Open\" , \"In Progress\" , \"Completed\" , \"Closed\" , \"Cancelled\"-->\n\t\t<upd:Resolution>{reason}</upd:Resolution> <!-- Mandatory : Resolution for update service request -->\n\t\t<upd:StatusReason>{reason}</upd:StatusReason> <!-- Mandatory : Incident Status updated reason -->\n               \t<upd:RootCause>{root_cause}</upd:RootCause><!-- Optional: Root Cause -->\n               \t<upd:RootCauseDetails>{root_casue_detail}</upd:RootCauseDetails> <!-- Optional: Root Cause reason -->\n            </upd:ServiceRequestSpecification>\n         </upd:ServiceRequestDetails>\n      </upd:UpdateServiceRequest>\n   </soapenv:Body>\n</soapenv:Envelope>"
        headers = {
            'Content-Type': "application/xml"
        }

        try:
            response = requests.request("POST", url, data=payload, headers=headers, timeout=3)
            self.log.log_info(
                f"api name: crm_complain_update,sr_number: {sr_id}, msisdn: {msisdn}, calling id : {id}, response: {response.text}")
            # print(response.text)
            tree = ElementTree.fromstring(response.text)
            ns = {"v2": "http://www.robi.com.bd/soa/xsd/UpdateServiceRequest/V2"}
            status_desc = tree.find('.//v2:StatusDesc', ns).text
            if status_desc == 'Success':
                self.log.log_info(
                    f"Response received from CRM Detail : MSISND - {msisdn} SR_ID - {sr_id} Status - {status}  ")
                print(response.text)
                return "Success"
            else:
                self.log.log_warn(
                    f"Unable to change status in CRM, CRM complain terminate not possible Details : For MSISDN - {msisdn} SR_ID - {sr_id} calling id : {id} Status - {status} Exception - {status_desc}")
                print(response.text)
                return "fail"

        except requests.exceptions.RequestException as e:
            self.log.log_critical(
                f"Unable to connect to CRM, CRM complain terminate not possible Details : For MSISDN - {msisdn} SR_ID - {sr_id} calling id : {id} Status - {status} Exception - {e}")
            print(
                f"Unable to connect to CRM, CRM complain terminate not possible Details : For MSISDN - {msisdn} SR_ID - {sr_id} calling id : {id} Status - {status} Exception - {e}")
            return "fail"

    def crm_complain_update_counter(self, msisdn, sr_id, current_status, target_status, error):
        time.sleep(1)
        init_msg = f"crm_complain_update_counter API Hit : (msisdn: {msisdn}, sr_id:{sr_id}, current_status:{current_status}, target_status:{target_status}, error:{error})"
        self.log.log_info(init_msg)
        print(init_msg)
        print(msisdn, sr_id, target_status)
        i = 0
        while i < 3:
            i = i + 1
            time.sleep(1)
            response = self.crm_complain_update(msisdn, sr_id, target_status, error=error)
            print(msisdn, sr_id, target_status)
            if response == "Success":
                self.log.log_info(response)
                print(response)
                return response
            else:
                if i == 3:
                    if response == "fail":
                        error_ = f"{error}, Complain's status can not be changed to {target_status}, Current status: {current_status}"
                        #   db.single_data_update(MSISDN=msisdn, SR_NUMBER=sr_id, ERROR=error_)
                        print(error_)
                    return response