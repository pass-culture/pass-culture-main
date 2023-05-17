from pcapi.core import mails
import pcapi.core.educational.models as educational_models
from pcapi.core.mails import models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


def send_new_request_made_by_redactor_to_ac(request: educational_models.CollectiveOfferRequest) -> bool:
    emails = request.collectiveOfferTemplate.bookingEmails
    if not emails:
        return True
    data = get_data_request_made_by_redactor_to_ac(request)
    main_recipient, bcc_recipients = emails[0], emails[1:]
    return mails.send(recipients=main_recipient, bcc_recipients=bcc_recipients, data=data)


def get_data_request_made_by_redactor_to_ac(
    request: educational_models.CollectiveOfferRequest,
) -> models.TransactionalEmailData:
    return models.TransactionalEmailData(
        template=TransactionalEmail.EAC_NEW_REQUEST_FOR_OFFER.value,
        params={
            "OFFER_NAME": request.collectiveOfferTemplate.name,
            "EVENT_DATE_REQUESTED": request.requestedDate,
            "TOTAL_STUDENTS": request.totalStudents,
            "TOTAL_TEACHERS": request.totalTeachers,
            "COMMENT": request.comment,
            "REDACTOR_NAME": request.educationalRedactor.firstName,
            "REDACTOR_LAST_NAME": request.educationalRedactor.lastName,
            "REDACTOR_MAIL": request.educationalRedactor.email,
            "REDACTOR_PHONE": request.phoneNumber,
        },
    )
