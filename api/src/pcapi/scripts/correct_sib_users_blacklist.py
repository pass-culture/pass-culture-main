# in v174.0.0, a regression has been introduced on users creation and update in sendinBlue.
# Indeed, a user email should be blacklisted on SiB when he decides not to receive the email notifications (attribute notificationSubscriptions.marketing_email = false)
# the "emailBlacklisted" field sent to sendinBlue was changed to : emailBlacklisted=notificationSubscriptions.marketing_email is not False.
# Hence this script will be used in staging and production to update users, added or modified after the 02/02/2022 (date of the commit - to make sure we do not forget users)
from pprint import pprint

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from pcapi import settings


def correct_sib_users_blacklist(limit: int):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
    offset = 0
    modified_since = "2022-02-10T00:00:00+01:00"
    try:
        api_response = api_instance.get_contacts(limit=limit, offset=offset, modified_since=modified_since)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling ContactsApi->get_contacts: %s\n" % e)
