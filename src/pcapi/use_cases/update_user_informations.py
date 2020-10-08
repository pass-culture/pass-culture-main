from datetime import datetime
from pcapi.repository.user_queries import find_user_by_id
from pcapi.repository import repository

class AlterableUserInformations(object):
    def __init__(self,
                 id: int,
                 cultural_survey_id: str = None,
                 cultural_survey_filled_date: datetime = None,
                 department_code: str = None,
                 email: str = None,
                 last_connection_date: datetime = None,
                 needs_to_fill_cultural_survey: bool = None,
                 phone_number: str = None,
                 postal_code: str = None,
                 public_name: str = None,
                 has_seen_tutorials: bool = None):
        self.id = id
        self.cultural_survey_id = cultural_survey_id
        self.cultural_survey_filled_date = cultural_survey_filled_date
        self.department_code = department_code
        self.email = email
        self.last_connection_date = last_connection_date
        self.needs_to_fill_cultural_survey = needs_to_fill_cultural_survey
        self.phone_number = phone_number
        self.postal_code = postal_code
        self.public_name = public_name
        self.has_seen_tutorials = has_seen_tutorials


def update_user_informations(user_informations: AlterableUserInformations):
    current_user = find_user_by_id(user_informations.id)
    if user_informations.cultural_survey_id is not None:
        current_user.culturalSurveyId = user_informations.cultural_survey_id

    if user_informations.cultural_survey_filled_date is not None:
        current_user.culturalSurveyFilledDate = user_informations.cultural_survey_filled_date

    if user_informations.department_code is not None:
        current_user.departementCode = user_informations.department_code

    if user_informations.email is not None:
        current_user.email = user_informations.email

    if user_informations.last_connection_date is not None:
        current_user.lastConnectionDate = user_informations.last_connection_date

    if user_informations.needs_to_fill_cultural_survey is not None:
        current_user.needsToFillCulturalSurvey = user_informations.needs_to_fill_cultural_survey

    if user_informations.phone_number is not None:
        current_user.phoneNumber = user_informations.phone_number

    if user_informations.postal_code is not None:
        current_user.postalCode = user_informations.postal_code

    if user_informations.public_name is not None:
        current_user.publicName = user_informations.public_name

    if user_informations.has_seen_tutorials is not None:
        current_user.hasSeenTutorials = user_informations.has_seen_tutorials
    repository.save(current_user)

    return current_user
