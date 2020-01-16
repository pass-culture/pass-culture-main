from connectors import api_entreprises
from repository.repository import Repository
from repository import venue_queries


def update_venue_with_sirene_data(data: dict, old_siret: str):
    parsed_data = _parse_sirene_data(data)
    venue = venue_queries.find_by_siret(old_siret)
    venue.siret = parsed_data.get('siret')
    venue.address = parsed_data.get('address') or venue.address
    venue.name = parsed_data.get('name') or venue.name
    venue.city = parsed_data.get('city') or venue.city
    venue.latitude = parsed_data.get('latitude') or venue.latitude
    venue.longitude = parsed_data.get('longitude') or venue.longitude
    venue.postalCode = parsed_data.get('postalCode') or venue.postalCode
    Repository.save(venue)


def _parse_sirene_data(data: dict) -> dict:
    field_equivalence = {
        "siret": "siret",
        "l1_normalisee": "name",
        "l1_declaree": "name",
        "l4_normalisee": "address",
        "libelle_commune": "city",
        "latitude": "latitude",
        "longitude": "longitude",
        "code_postal": "postalCode",
    }

    if "l1_normalisee" in field_equivalence:
        field_equivalence.pop("l1_declaree")
    return {equivalence: data['etablissement'][key] for key, equivalence in field_equivalence.items() if
            key in data['etablissement']}


def update_venue(old_siret: str, new_siret: str):
    api_sirene_response = api_entreprises.get_by_siret(new_siret)
    update_venue_with_sirene_data(api_sirene_response.json(), old_siret)
