from enum import Enum

from pcapi.core.mails import models


class TransactionalEmail(Enum):
    # Empty tags when it is set directly in Sendinblue template

    ACCEPTED_AS_BENEFICIARY_V3 = models.Template(id_prod=1452, id_not_prod=176, use_priority_queue=True)
    # --- Obsolete - use ACCEPTED_AS_BENEFICIARY_V3 and BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER_V3 instead ---
    ACCEPTED_AS_BENEFICIARY = models.Template(id_prod=96, id_not_prod=25, use_priority_queue=True)
    ACCEPTED_AS_EAC_BENEFICIARY = models.Template(id_prod=257, id_not_prod=27, use_priority_queue=True)
    BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER = models.Template(id_prod=78, id_not_prod=32, send_to_ehp=False)
    # --- end of obsolete ---
    ACCOUNT_UNSUSPENDED = models.Template(id_prod=644, id_not_prod=87, tags=["reactivation_compte_utilisateur"])
    BIRTHDAY_AGE_17_TO_NEWLY_ELIGIBLE_USER = models.Template(id_prod=1482, id_not_prod=178, send_to_ehp=True)
    BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER_V3 = models.Template(id_prod=1483, id_not_prod=179, send_to_ehp=True)
    BOOKING_CANCELLATION_BY_BENEFICIARY = models.Template(
        id_prod=223, id_not_prod=33, tags=["jeunes_offre_annulee_jeune"]
    )
    BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY = models.Template(
        id_prod=225, id_not_prod=161, tags=["jeunes_offre_annulee_pros"], send_to_ehp=False
    )
    BOOKING_CONFIRMATION_BY_BENEFICIARY = models.Template(
        id_prod=725, id_not_prod=96, tags=["jeunes_reservation_confirmee_v3"]
    )
    BOOKING_EVENT_REMINDER_TO_BENEFICIARY = models.Template(id_prod=665, id_not_prod=82)
    BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY = models.Template(
        id_prod=224, id_not_prod=36, tags=["jeunes_offre_reportee_pro"], send_to_ehp=False
    )
    BOOKING_SOON_TO_BE_EXPIRED_TO_BENEFICIARY = models.Template(id_prod=144, id_not_prod=42, send_to_ehp=False)
    COMPLETE_SUBSCRIPTION_AFTER_DMS = models.Template(
        id_prod=679, id_not_prod=84, tags=["jeunes_complete_inscription_apres_dms"]
    )
    CREATE_ACCOUNT_AFTER_DMS = models.Template(id_prod=678, id_not_prod=85, tags=["jeunes_creation_compte_apres_dms"])
    EMAIL_ALREADY_EXISTS = models.Template(id_prod=617, id_not_prod=79, tags=["email_existant_en_base"])
    EMAIL_CHANGE_CONFIRMATION = models.Template(
        id_prod=253, id_not_prod=134, tags=["changement_email_confirmation"], use_priority_queue=True
    )
    EMAIL_CHANGE_CANCELLATION = models.Template(id_prod=1001, id_not_prod=136, use_priority_queue=True)
    EMAIL_CHANGE_REQUEST = models.Template(
        id_prod=142, id_not_prod=133, tags=["changement_email_demande"], use_priority_queue=True
    )
    EMAIL_CHANGE_INFORMATION = models.Template(
        id_prod=944, id_not_prod=135, tags=["changement_email_information"], use_priority_queue=True
    )
    EMAIL_CONFIRMATION = models.Template(
        id_prod=201, id_not_prod=15, tags=["jeunes_confirmation_mail"], use_priority_queue=True
    )
    ONLINE_EVENT_REMINDER = models.Template(id_prod=1092, id_not_prod=154, send_to_ehp=False)
    EXPIRED_BOOKING_TO_BENEFICIARY = models.Template(id_prod=145, id_not_prod=34, send_to_ehp=False)
    FRAUD_SUSPICION = models.Template(id_prod=82, id_not_prod=24)
    NEW_PASSWORD_REQUEST = models.Template(id_prod=141, id_not_prod=26, use_priority_queue=True)
    NEW_PASSWORD_REQUEST_FOR_SUSPICIOUS_LOGIN = models.Template(
        id_prod=1108, id_not_prod=155, tags=["jeunes_nouveau_mdp_connexion_suspicieuse"], use_priority_queue=True
    )
    OFFER_WEBAPP_LINK_TO_IOS_USER = models.Template(
        id_prod=476, id_not_prod=45, tags=["redirect_ios"], use_priority_queue=True
    )
    OFFER_WITHDRAWAL_UPDATED_BY_PRO = models.Template(id_prod=868, id_not_prod=121)
    PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY = models.Template(
        id_prod=510, id_not_prod=53, tags=["jeunes_erreur_importation_dms"]
    )
    RECREDIT_TO_UNDERAGE_BENEFICIARY = models.Template(
        id_prod=303, id_not_prod=31, tags=["anniversaire_16_17_ans"], send_to_ehp=False
    )
    RECREDIT = models.Template(id_prod=1509, id_not_prod=180, send_to_ehp=False)
    REPORTED_OFFER_BY_USER = models.Template(id_prod=589, id_not_prod=70)
    SUBSCRIPTION_FOREIGN_DOCUMENT_ERROR = models.Template(
        id_prod=385, id_not_prod=40, tags=["jeunes_document_etranger"]
    )
    SUBSCRIPTION_INFORMATION_ERROR = models.Template(id_prod=410, id_not_prod=43)
    SUBSCRIPTION_INVALID_DOCUMENT_ERROR = models.Template(id_prod=384, id_not_prod=39)
    SUBSCRIPTION_NOT_AUTHENTIC_DOCUMENT_ERROR = models.Template(id_prod=760, id_not_prod=101)
    SUBCRIPTION_REJECTED_FOR_DUPLICATE_BENEFICIARY = models.Template(id_prod=80, id_not_prod=77)
    SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR = models.Template(
        id_prod=304, id_not_prod=38, tags=["jeunes_document_illisible"]
    )
    SUSPICIOUS_LOGIN = models.Template(id_prod=964, id_not_prod=129)
    USER_REQUEST_DELETE_ACCOUNT_RECEPTION = models.Template(
        id_prod=511, id_not_prod=54, tags=["reception_demande_suppression_compte_jeune"]
    )
    NOTIFICATION_BEFORE_DELETING_SUSPENDED_ACCOUNT = models.Template(
        id_prod=1004, id_not_prod=144, tags=["notification_avant_suppression_compte_suspendu"]
    )
    BENEFICIARY_PRE_ANONYMIZATION = models.Template(id_prod=1388, id_not_prod=166)
    PERSONAL_DATA_UPDATED_FROM_BACKOFFICE = models.Template(id_prod=1393, id_not_prod=169, use_priority_queue=True)
    UPDATE_REQUEST_MARKED_WITHOUT_CONTINUATION = models.Template(id_prod=1442, id_not_prod=174)
    UPDATE_REQUEST_ASK_FOR_CORRECTION = models.Template(id_prod=1441, id_not_prod=175)

    # UBBLE KO REMINDER
    UBBLE_KO_REMINDER_ID_CHECK_DATA_MATCH = models.Template(id_prod=824, id_not_prod=116)
    UBBLE_KO_REMINDER_ID_CHECK_EXPIRED = models.Template(id_prod=831, id_not_prod=118)
    UBBLE_KO_REMINDER_ID_CHECK_NOT_AUTHENTIC = models.Template(id_prod=821, id_not_prod=117)
    UBBLE_KO_REMINDER_ID_CHECK_NOT_SUPPORTED = models.Template(id_prod=825, id_not_prod=119)
    UBBLE_KO_REMINDER_ID_CHECK_UNPROCESSABLE = models.Template(id_prod=823, id_not_prod=115)

    # PRO EMAIL
    BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO = models.TemplatePro(id_prod=39, id_not_prod=38)
    BOOKING_CANCELLATION_CONFIRMATION_BY_PRO = models.TemplatePro(id_prod=40, id_not_prod=39)
    BOOKING_EXPIRATION_TO_PRO = models.TemplatePro(id_prod=38, id_not_prod=37, send_to_ehp=False)
    EAC_NEW_BOOKING_TO_PRO = models.TemplatePro(id_prod=18, id_not_prod=18)
    EAC_NEW_PREBOOKING_TO_PRO = models.TemplatePro(id_prod=19, id_not_prod=19)
    EAC_ONE_DAY_AFTER_EVENT = models.TemplatePro(id_prod=24, id_not_prod=25, send_to_ehp=False)
    EAC_ONE_DAY_BEFORE_EVENT = models.TemplatePro(id_prod=23, id_not_prod=23, send_to_ehp=False)
    EAC_PENDING_BOOKING_WITH_BOOKING_LIMIT_DATE_3_DAYS = models.TemplatePro(
        id_prod=22, id_not_prod=22, send_to_ehp=False
    )
    EAC_NEW_REQUEST_FOR_OFFER = models.TemplatePro(id_prod=54, id_not_prod=41)
    EAC_OFFERER_ACTIVATION_EMAIL = models.TemplatePro(id_prod=7, id_not_prod=7, send_to_ehp=False)
    EDUCATIONAL_BOOKING_CANCELLATION = models.TemplatePro(id_prod=17, id_not_prod=17, send_to_ehp=False)
    SIGNUP_EMAIL_CONFIRMATION_TO_PRO = models.TemplatePro(id_prod=6, id_not_prod=6)
    EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO = models.TemplatePro(id_prod=37, id_not_prod=36)
    PRO_EMAIL_CHANGE_CONFIRMATION = models.TemplatePro(id_prod=14, id_not_prod=14, use_priority_queue=True)
    PRO_EMAIL_CHANGE_REQUEST = models.TemplatePro(id_prod=15, id_not_prod=15, use_priority_queue=True)
    FIRST_VENUE_APPROVED_OFFER_TO_PRO = models.TemplatePro(id_prod=4, id_not_prod=4)
    FIRST_VENUE_BOOKING_TO_PRO = models.TemplatePro(id_prod=20, id_not_prod=20)
    INVOICE_AVAILABLE_TO_PRO = models.TemplatePro(id_prod=27, id_not_prod=27)
    NEW_BOOKING_TO_PRO = models.TemplatePro(id_prod=21, id_not_prod=21)
    NEW_OFFERER_VALIDATION = models.TemplatePro(id_prod=3, id_not_prod=3)
    NEW_OFFERER_REJECTION = models.TemplatePro(id_prod=8, id_not_prod=8)
    OFFER_APPROVAL_TO_PRO = models.TemplatePro(id_prod=31, id_not_prod=31)
    OFFERER_ATTACHMENT_INVITATION_NEW_USER = models.TemplatePro(id_prod=48, id_not_prod=51)
    OFFERER_ATTACHMENT_INVITATION_EXISTING_VALIDATED_USER_EMAIL = models.TemplatePro(id_prod=46, id_not_prod=49)
    OFFERER_ATTACHMENT_INVITATION_EXISTING_NOT_VALIDATED_USER_EMAIL = models.TemplatePro(id_prod=47, id_not_prod=50)
    OFFERER_ATTACHMENT_INVITATION_ACCEPTED = models.TemplatePro(id_prod=45, id_not_prod=48)
    OFFER_REJECTION_TO_PRO = models.TemplatePro(id_prod=30, id_not_prod=30)
    OFFER_PENDING_TO_REJECTED_TO_PRO = models.TemplatePro(id_prod=34, id_not_prod=34)
    OFFER_VALIDATED_TO_REJECTED_TO_PRO = models.TemplatePro(id_prod=35, id_not_prod=35)
    OFFERER_ATTACHMENT_VALIDATION = models.TemplatePro(id_prod=2, id_not_prod=2)
    OFFERER_ATTACHMENT_REJECTION = models.TemplatePro(id_prod=9, id_not_prod=9)
    OFFERER_CLOSED = models.TemplatePro(id_prod=123, id_not_prod=61)
    REMINDER_OFFERER_INDIVIDUAL_SUBSCRIPTION = models.TemplatePro(id_prod=16, id_not_prod=16)
    REMINDER_7_DAYS_BEFORE_EVENT_TO_PRO = models.TemplatePro(id_prod=36, id_not_prod=24)
    REMINDER_OFFER_CREATION_5_DAYS_AFTER_TO_PRO = models.TemplatePro(
        id_prod=13,
        id_not_prod=13,
        enable_unsubscribe=True,
    )
    REMINDER_OFFER_CREATION_10_DAYS_AFTER_TO_PRO = models.TemplatePro(
        id_prod=12,
        id_not_prod=12,
        enable_unsubscribe=True,
    )
    RESET_PASSWORD_TO_PRO = models.TemplatePro(id_prod=5, id_not_prod=5)
    RESET_PASSWORD_TO_CONNECTED_PRO = models.TemplatePro(id_prod=11, id_not_prod=11)
    WELCOME_TO_PRO = models.TemplatePro(id_prod=1, id_not_prod=1)
    VENUE_NEEDS_PICTURE = models.TemplatePro(id_prod=10, id_not_prod=10)
    VENUE_SYNC_DISABLED = models.TemplatePro(id_prod=33, id_not_prod=33)
    VENUE_SYNC_DELETED = models.TemplatePro(id_prod=32, id_not_prod=32)
    VENUE_BANK_ACCOUNT_LINK_DEPRECATED = models.TemplatePro(id_prod=29, id_not_prod=29)
    BANK_ACCOUNT_VALIDATED = models.TemplatePro(id_prod=28, id_not_prod=28)
    EXTERNAL_BOOKING_SUPPORT_CANCELLATION = models.TemplatePro(id_prod=26, id_not_prod=26)

    # Finance incidents
    RETRIEVE_INCIDENT_AMOUNT_ON_INDIVIDUAL_BOOKINGS = models.TemplatePro(id_prod=77, id_not_prod=54)
    RETRIEVE_INCIDENT_AMOUNT_ON_COLLECTIVE_BOOKINGS = models.TemplatePro(id_prod=78, id_not_prod=55)
    RETRIEVE_DEBIT_NOTE_ON_INDIVIDUAL_BOOKINGS = models.TemplatePro(id_prod=119, id_not_prod=60)
    COMMERCIAL_GESTURE_REIMBURSEMENT = models.TemplatePro(id_prod=80, id_not_prod=56)

    PROVIDER_REIMBURSEMENT_CSV = models.TemplatePro(id_prod=81, id_not_prod=57)
