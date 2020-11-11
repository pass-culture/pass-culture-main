from typing import Dict


def get_application_by_detail_response(
    address: str = "18 avenue des fleurs",
    application_id: int = 2,
    birth_date: str = "09/08/1995",
    city: str = "RENNES",
    email: str = "rennes@example.org",
    first_name: str = "Céline",
    gender: str = "F",
    last_name: str = "DURAND",
    phone_number: str = "0123456789",
    postal_code: str = "35123",
    status: str = "Apprenti",
) -> Dict:
    return {
        "registrationDate": "04/06/2020 06:00",
        "id": application_id,
        "address": address,
        "birthDate": birth_date,
        "city": city,
        "email": email,
        "firstName": first_name,
        "gender": gender,
        "lastName": last_name,
        "postalCode": postal_code,
        "phoneNumber": phone_number,
        "activity": status,
    }


def get_token_detail_response(token: str) -> Dict:
    return {"Value": token}
