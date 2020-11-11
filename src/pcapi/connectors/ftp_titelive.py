import ftplib
from io import BytesIO
import os
from typing import List
from typing import Pattern
from zipfile import ZipFile

from pcapi.domain.titelive import put_today_file_at_end_of_list
from pcapi.utils.logger import logger


FTP_TITELIVE_URI = os.environ.get("FTP_TITELIVE_URI")
FTP_TITELIVE_USER = os.environ.get("FTP_TITELIVE_USER")
FTP_TITELIVE_PWD = os.environ.get("FTP_TITELIVE_PWD")


def get_titelive_ftp():
    if FTP_TITELIVE_URI is None:
        raise ValueError("URI du FTP Titelive non spécifiée.")
    return ftplib.FTP(FTP_TITELIVE_URI)


def connect_to_titelive_ftp():
    ftp_titelive = get_titelive_ftp()
    if FTP_TITELIVE_USER is None or FTP_TITELIVE_PWD is None:
        raise ValueError("Informations de connexion au FTP Titelive non spécifiée.")
    ftp_titelive.login(FTP_TITELIVE_USER, FTP_TITELIVE_PWD)
    return ftp_titelive


def get_zip_file_from_ftp(zip_file_name: str, folder_name: str) -> ZipFile:
    data_file = BytesIO()
    data_file.name = zip_file_name
    file_path = "RETR " + folder_name + "/" + zip_file_name
    logger.info("  Downloading file " + file_path)
    connect_to_titelive_ftp().retrbinary(file_path, data_file.write)
    return ZipFile(data_file, "r")


def get_files_to_process_from_titelive_ftp(titelive_folder_name: str, date_regexp: Pattern[str]) -> List[str]:
    ftp_titelive = connect_to_titelive_ftp()
    files_list = ftp_titelive.nlst(titelive_folder_name)

    files_list_matching_regex = [file_name for file_name in files_list if date_regexp.search(str(file_name))]
    sorted_files_list = sorted(files_list_matching_regex)

    # We want today file to be the last element of the list
    # in order to save up-to-date data during last iteration
    ordered_files_to_process = put_today_file_at_end_of_list(sorted_files_list, date_regexp)

    return ordered_files_to_process
