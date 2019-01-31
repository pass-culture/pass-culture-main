import ftplib
import os

FTP_TITELIVE_URI = os.environ.get("FTP_TITELIVE_URI")
FTP_TITELIVE_USER = os.environ.get("FTP_TITELIVE_USER")
FTP_TITELIVE_PWD = os.environ.get("FTP_TITELIVE_PWD")

FTP_TITELIVE = ftplib.FTP(FTP_TITELIVE_URI)


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
