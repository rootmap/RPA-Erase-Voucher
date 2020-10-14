import json
import os
import shutil
import sys
import time
from datetime import datetime
from utils.logger import Logger
from apps.config import ConfigParser


class AppUtils:
    log = Logger.get_instance()
    configParser = ConfigParser()
    conf = configParser.get_config()

    @staticmethod
    def new_file_name():
        now = datetime.now()
        dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
        AppUtils.log.log_info(msg="New Moved File Name TimeStamp= " + str(dt_string))
        return dt_string

    @staticmethod
    def get_current_time():
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        AppUtils.log.log_info(msg="Current Time =" + str(dt_string))
        return dt_string

    @staticmethod
    def rpa_running_flag(flag='Start'):
        AppUtils.log.log_info(msg="RPA " + flag + " Time = " + str(AppUtils.get_current_time()))
        return

    @staticmethod
    def get_download_path():
        time.sleep(3)
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            print("Location = "+str(location))
            return location
        else:
            print("Location = " + str(os.path.join(os.path.expanduser('~'), 'downloads')))
            return os.path.join(os.path.expanduser('~'), 'downloads')

    @staticmethod
    def move_downloaded_file(file_name=''):
        filename = max([AppUtils.get_download_path() + "\\" + f for f in os.listdir(AppUtils.get_download_path())],
                       key=os.path.getctime)
        print("Downloaded File = " + str(filename))
        new_file_name = AppUtils.conf['rpa_name'] + "_" + file_name + ".csv"
        shutil.move(filename, os.path.join(AppUtils.conf['crm_download_file_directory'], r"" + new_file_name))
        return new_file_name

    @staticmethod
    def newest_file_downloaded():
        time.sleep(3)
        files = os.listdir(AppUtils.get_download_path())
        paths = [os.path.join(AppUtils.get_download_path(), basename) for basename in files]
        file_downloaded = ''
        try:
            max(paths, key=os.path.getctime)
            file_downloaded = max(paths, key=os.path.getctime)
            return file_downloaded
        except Exception as e:
            print(e)
            time.sleep(3)
            print('Waiting 3 Second to get files from download....')
            AppUtils.newest_file_downloaded()
