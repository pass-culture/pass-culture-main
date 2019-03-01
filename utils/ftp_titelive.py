import ftplib
import os
from datetime import datetime
from zipfile import ZipFile

from io import BytesIO

from utils.logger import logger

FTP_TITELIVE_URI = os.environ.get("FTP_TITELIVE_URI")
FTP_TITELIVE_USER = os.environ.get("FTP_TITELIVE_USER")
FTP_TITELIVE_PWD = os.environ.get("FTP_TITELIVE_PWD")

TITELIVE_THINGS_DATE_FORMAT = "%d/%m/%Y"
TITELIVE_DESCRIPTION_DATE_FORMAT = "%y%m%d"
TITELIVE_STOCK_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def read_description_date(date):
    return datetime.strptime(date, TITELIVE_DESCRIPTION_DATE_FORMAT)


def read_date(date):
    return datetime.strptime(date, TITELIVE_THINGS_DATE_FORMAT)


def read_stock_datetime(date):
    return datetime.strptime(date, TITELIVE_STOCK_DATETIME_FORMAT)


def get_titelive_ftp():
    if FTP_TITELIVE_URI is None:
        raise ValueError('URI du FTP Titelive non spécifiée.')
    return ftplib.FTP(FTP_TITELIVE_URI)


def connect_to_titelive_ftp():
    ftp_titelive = get_titelive_ftp()
    if FTP_TITELIVE_USER is None \
            or FTP_TITELIVE_PWD is None:
        raise ValueError('Informations de connexion au FTP Titelive non spécifiée.')
    ftp_titelive.login(FTP_TITELIVE_USER, FTP_TITELIVE_PWD)
    return ftp_titelive


def get_date_from_filename(filename, date_regexp):
    if isinstance(filename, ZipFile):
        real_filename = filename.filename
    else:
        real_filename = filename
    match = date_regexp.search(str(real_filename))
    if not match:
        raise ValueError('Invalid filename in Titelive folder : %s' % filename)
    return int(match.groups()[-1])


def put_today_file_at_end_of_list(ordered_files_list, date_regexp):
    today = datetime.utcnow().day
    files_after_today = list(filter(lambda f: get_date_from_filename(f, date_regexp) > today,
                                    ordered_files_list))
    files_before_today = list(filter(lambda f: get_date_from_filename(f, date_regexp) <= today,
                                     ordered_files_list))
    return files_after_today + files_before_today


def get_files_to_process_from_titelive_ftp(titelive_folder_name, date_regexp):
    ftp_titelive = connect_to_titelive_ftp()
    files_list = ftp_titelive.nlst(titelive_folder_name)

    files_list_matching_regex = [file_name for file_name in files_list if date_regexp.search(str(file_name))]
    ordered_files_list = sorted(files_list_matching_regex)

    # We want today file to be the last element of the list
    # in order to save up-to-date data during last iteration
    ordered_files_to_process = put_today_file_at_end_of_list(ordered_files_list, date_regexp)

    return ordered_files_to_process


def get_zip_file_from_ftp(zip_file_name, folder_name):
    data_file = BytesIO()
    data_file.name = zip_file_name
    file_path = 'RETR ' + folder_name + '/' + zip_file_name
    logger.info("  Downloading file " + file_path)
    get_titelive_ftp().retrbinary(file_path, data_file.write)
    return ZipFile(data_file, 'r')
