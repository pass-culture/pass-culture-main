import csv
import logging

from pcapi.repository.offerer_queries import find_by_siren
from pcapi.models import ApiKey
from pcapi.utils.token import random_token
from pcapi.repository import repository


logger = logging.getLogger(__name__)

def create_api_key_from_csv(row: dict) -> None:
    siret = row['siret']
    siren = siret[0:9]
    offerer = find_by_siren(siren)
    if not offerer:
        logger.info("offerer not found with SIRET %s", siret)
        return siret, 'offerer not found'
    has_already_an_api_key = ApiKey.query.filter(ApiKey.offererId == offerer.id).first()
    if has_already_an_api_key:
        logger.info("offerer has already an api key for SIRET %s", siret)
        return siret, has_already_an_api_key.value
    api_key = ApiKey()
    api_key.offererId = offerer.id
    api_key.value = random_token(64)
    repository.save(api_key)
    logger.info("api_key created for SIRET %s", siret)
    return siret, api_key.value

def create_from_csv_file(csv_file_path: str) -> None:
    saved_data = []
    with open(csv_file_path) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            saved_data.append(create_api_key_from_csv(row))
    with open('./siret_and_api_key.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        for row in saved_data:
            writer.writerow(row)

create_from_csv_file('./siret_for_api_key.csv')
