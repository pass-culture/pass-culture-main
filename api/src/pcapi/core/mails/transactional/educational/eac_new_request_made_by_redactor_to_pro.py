from pcapi import settings
from pcapi.core import mails
import pcapi.core.educational.models as educational_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_new_request_made_by_redactor_to_pro(request: educational_models.CollectiveOfferRequest) -> None:
    emails = request.collectiveOfferTemplate.bookingEmails
    if not emails:
        return
    data = get_data_request_made_by_redactor_to_pro(request)
    main_recipient, bcc_recipients = emails[0], emails[1:]
    mails.send(recipients=main_recipient, bcc_recipients=bcc_recipients, data=data)


def get_data_request_made_by_redactor_to_pro(
    request: educational_models.CollectiveOfferRequest,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.EAC_NEW_REQUEST_FOR_OFFER.value,
        params={
            "OFFER_NAME": request.collectiveOfferTemplate.name,
            "VENUE_NAME": request.collectiveOfferTemplate.venue.common_name,
            "EVENT_DATE": request.requestedDate.strftime("%d/%m/%Y") if request.requestedDate else "",
            "NB_STUDENTS": request.totalStudents,
            "NB_TEACHERS": request.totalTeachers,
            "REQUEST_COMMENT": request.comment,
            "EDUCATIONAL_INSTITUTION_NAME": request.educationalInstitution.name,
            "CITY_NAME": request.educationalInstitution.city,
            "INSTITUTION_ZIP_CODE": request.educationalInstitution.postalCode,
            "REDACTOR_FIRSTNAME": request.educationalRedactor.firstName,
            "REDACTOR_LASTNAME": request.educationalRedactor.lastName,
            "REDACTOR_EMAIL": request.educationalRedactor.email,
            "REDACTOR_PHONE_NUMBER": request.phoneNumber,
            "OFFER_CREATION_URL": f"{settings.PRO_URL}/offre/collectif/creation/{request.collectiveOfferTemplateId}/requete/{request.id}",
            "OFFERER_ID": request.collectiveOfferTemplate.venue.managingOffererId,
            "VENUE_ID": request.collectiveOfferTemplate.venue.id,
        },
    )
