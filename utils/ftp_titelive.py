import ftplib
import os
from datetime import datetime

from utils.logger import logger

FTP_TITELIVE_URI = os.environ.get("FTP_TITELIVE_URI")
FTP_TITELIVE_USER = os.environ.get("FTP_TITELIVE_USER")
FTP_TITELIVE_PWD = os.environ.get("FTP_TITELIVE_PWD")

FTP_TITELIVE = ftplib.FTP(FTP_TITELIVE_URI)

TITELIVE_DATE_FORMAT = "%d/%m/%Y"
TITELIVE_DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"


def read_date(date):
    return datetime.strptime(date, TITELIVE_DATE_FORMAT)


def read_datetime(date):
    return datetime.strptime(date, TITELIVE_DATETIME_FORMAT)


def get_titelive_ftp():
    if FTP_TITELIVE_URI is None \
            or FTP_TITELIVE_USER is None \
            or FTP_TITELIVE_PWD is None:
        raise ValueError('Information de connexion au FTP Titelive non spécifiée.')
    return FTP_TITELIVE


def connect_to_titelive_ftp():
    ftp_titelive = get_titelive_ftp()
    ftp_titelive.login(FTP_TITELIVE_USER, FTP_TITELIVE_PWD)
    return ftp_titelive


def get_date_from_thing_filename(filename, date_regexp):
    match = date_regexp.search(str(filename))
    if not match:
        raise ValueError('Invalid filename in Titelive folder : %s' % filename)
    return int(match.group(2))


def get_ordered_thing_files_from_titelive_ftp(titelive_folder_name, date_regexp):
    ftp_titelive = connect_to_titelive_ftp()
    files_list = ftp_titelive.nlst(titelive_folder_name)
    logger.info("COUCOU !!!")

    files_list_final = [file_name for file_name in files_list if date_regexp.search(str(file_name))]

    all_thing_files = sorted(files_list_final)
    today = datetime.utcnow().day
    # Titelive 'Quotidien' files stay on the server only for about
    # 26 days. A file with today's date can therefore only be from
    # today, and should always be imported last
    return list(filter(lambda f: get_date_from_thing_filename(f, date_regexp) > today,
                       all_thing_files)) \
           + list(filter(lambda f: get_date_from_thing_filename(f, date_regexp) <= today,
                         all_thing_files))
