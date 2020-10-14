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


class ConfigParser:

    def __init__(self):
        with open("./env_config.json") as config_file:
            conf = json.load(config_file)

        self.conf = conf

    @staticmethod
    def stop_execution():
        print('Stopping Execution')
        sys.exit('Stopping Execution')

    def encrypt_key(self, key):
        pass_phase = self.conf['PassPhase']
        encrypted = CryptoPassPhase.encrypt(pass_phase, key)
        print(encrypted)
        self.stop_execution()

    def get_credentials(self):
        link = self.conf['crm_link']
        pass_phase = self.conf['PassPhase']
        interaction_type = self.conf['interaction_type']
        ins_product = self.conf['ins_product']
        ins_area = self.conf['ins_area']
        ins_sub_area = self.conf['ins_sub_area']
        ins_status = self.conf['ins_status']
        crm_username = CryptoPassPhase.decrypt(pass_phase, self.conf['crm_username'])
        crm_password = CryptoPassPhase.decrypt(pass_phase, self.conf['crm_password'])
        credentials = pd.DataFrame(
            columns=[
                "link",
                "username",
                "password",
                "interaction_type",
                "ins_product",
                "ins_area",
                "ins_sub_area",
                "ins_status"
            ],
            data=[
                [
                    link,
                    crm_username,
                    crm_password,
                    interaction_type,
                    ins_product,
                    ins_area,
                    ins_sub_area,
                    ins_status
                ]
            ]
        )
        return credentials

    def get_reporting_email(self):
        pass

    def get_config(self):
        return self.conf
