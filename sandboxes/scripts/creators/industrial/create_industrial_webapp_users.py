import uuid
from datetime import datetime, timedelta

from repository import repository
from model_creators.generic_creators import create_user
from utils.logger import logger

departement_codeS = ["93", "97"]
WEBAPP_TAGS = [
    "has-signed-up",
    "has-filled-cultural-survey",
    "has-booked-activation",
    "has-confirmed-activation",
    "has-booked-some",
    "has-no-more-money"
]


def create_industrial_webapp_users():
    logger.info('create_industrial_webapp_users')

    users_by_name = {}

    validation_prefix, validation_suffix = 'AZERTY', 123
    validation_suffix += 1

    for departement_code in departement_codeS:

        for tag in WEBAPP_TAGS:
            short_tag = "".join([chunk[0].upper() for chunk in tag.split('-')])

            if tag == "has-signed-up":
                reset_password_token = '{}{}'.format(validation_prefix, validation_suffix)
                validation_suffix += 1
            else:
                reset_password_token = None

            cultural_survey_id = None
            needs_to_fill_cultural_survey = False
            has_seen_tutorials = True

            if tag == "has-filled-cultural-survey":
                has_seen_tutorials = False

            if tag == "has-signed-up":
                cultural_survey_id = uuid.uuid4()
                needs_to_fill_cultural_survey = True
                has_seen_tutorials = False

            email = "pctest.jeune{}.{}@btmx.fr".format(departement_code, tag)

            users_by_name['jeune{} {}'.format(departement_code, tag)] = create_user(
                cultural_survey_id=cultural_survey_id,
                departement_code=str(departement_code),
                email=email,
                first_name="PC Test Jeune",
                has_seen_tutorials=has_seen_tutorials,
                last_name="{} {}".format(departement_code, short_tag),
                needs_to_fill_cultural_survey=needs_to_fill_cultural_survey,
                postal_code="{}100".format(departement_code),
                public_name="PC Test Jeune {} {}".format(departement_code, short_tag),
                reset_password_token=reset_password_token,
                reset_password_token_validity_limit=datetime.utcnow() + timedelta(hours=24))

    repository.save(*users_by_name.values())

    logger.info('created {} users'.format(len(users_by_name)))

    return users_by_name
