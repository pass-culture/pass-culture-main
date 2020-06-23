from typing import Dict


def get_application_by_detail_response(
        address: str = '18 avenue des fleurs',
        application_id: int = 2,
        birth_date: str = '09/08/1995',
        city: str = 'RENNES',
        email: str = 'rennes@example.org',
        first_name: str = 'Céline',
        gender: str = 'F',
        last_name: str = 'DURAND',
        phone_number: str = '0123456789',
        postal_code: str = '35123',
        status: str = 'Apprenti',
) -> Dict:
    return {
        'mtd_datEnreg': '04/06/2020 06:00',
        'mtd_jeuneID': application_id,
        'mtd_adrResid': address,
        'mtd_datNaiss': birth_date,
        'mtd_comResid': city,
        'mtd_mail': email,
        'mtd_prenom': first_name,
        'mtd_sexe': gender,
        'mtd_nom': last_name,
        'mtd_codPos': postal_code,
        'mtd_tel': phone_number,
        'mtd_statut': status
    }


def get_token_detail_response(token: str) -> Dict:
    return {
        'Value': token
    }
