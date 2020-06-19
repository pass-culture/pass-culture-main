from pyparsing import Dict


def get_application_by_detail_response(
        address: str = '18 avenue des fleurs',
        birth_date: str = '09/08/1995',
        city: str = 'RENNES',
        department_code: str = '35123',
        email: str = 'rennes@example.org',
        first_name: str = 'Céline',
        gender: str = 'F',
        last_name: str = 'DURAND',
        phone_number: str = '0123456789',
        status: str = 'Apprenti',
) -> Dict:
    return {
        'mtd_adrResid': address,
        'mtd_codPos': department_code,
        'mtd_comResid': city,
        'mtd_datEnreg': '04/06/2020 06:00',
        'mtd_datNaiss': birth_date,
        'mtd_jeuneID': 2,
        'mtd_mail': email,
        'mtd_nom': last_name,
        'mtd_prenom': first_name,
        'mtd_sexe': gender,
        'mtd_statut': status,
        'mtd_tel': phone_number
    }


def get_token_detail_response(token: str) -> Dict:
    return {
        'Value': token
    }
