from enum import Enum

from pcapi.core.mails import models


class TransactionalEmail(Enum):
    # Empty tags when it is set directly in Sendinblue template
    ACCEPTED_AS_BENEFICIARY = models.Template(id_prod=96, id_not_prod=25, use_priority_queue=True)
    ACCEPTED_AS_EAC_BENEFICIARY = models.Template(id_prod=257, id_not_prod=27, use_priority_queue=True)
    ACCOUNT_UNSUSPENDED = models.Template(id_prod=644, id_not_prod=87, tags=["reactivation_compte_utilisateur"])
    BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER = models.Template(id_prod=78, id_not_prod=32, send_to_ehp=False)
    BOOKING_CANCELLATION_BY_BENEFICIARY = models.Template(
        id_prod=223, id_not_prod=33, tags=["jeunes_offre_annulee_jeune"]
    )
    BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY = models.Template(
        id_prod=225, id_not_prod=161, tags=["jeunes_offre_annulee_pros"], send_to_ehp=False
    )
    BOOKING_CONFIRMATION_BY_BENEFICIARY = models.Template(
        id_prod=725, id_not_prod=96, tags=["jeunes_reservation_confirmee_v3"]
    )
    BOOKING_EVENT_REMINDER_TO_BENEFICIARY = models.Template(
        id_prod=665, id_not_prod=82, tags=["jeunes_rappel_evenement_j-1"]
    )
    BOOKING_EVENT_REMINDER_TO_BENEFICIARY_WITH_METADATA = models.Template(
        id_prod=1127, id_not_prod=124, tags=["jeunes_rappel_evenement_j-1"]
    )
    BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY = models.Template(
        id_prod=224, id_not_prod=36, tags=["jeunes_offre_reportee_pro"], send_to_ehp=False
    )
    BOOKING_SOON_TO_BE_EXPIRED_TO_BENEFICIARY = models.Template(
        id_prod=144, id_not_prod=42, send_to_ehp=False, tags=["jeunes_reservation_bientot_expiree"]
    )
    COMPLETE_SUBSCRIPTION_AFTER_DMS = models.Template(
        id_prod=679, id_not_prod=84, tags=["jeunes_complete_inscription_apres_dms"]
    )
    CREATE_ACCOUNT_AFTER_DMS = models.Template(id_prod=678, id_not_prod=85, tags=["jeunes_creation_compte_apres_dms"])
    EMAIL_ALREADY_EXISTS = models.Template(id_prod=617, id_not_prod=79, tags=["email_existant_en_base"])
    EMAIL_CHANGE_CONFIRMATION = models.Template(
        id_prod=253, id_not_prod=134, tags=["changement_email_confirmation"], use_priority_queue=True
    )
    EMAIL_CHANGE_CANCELLATION = models.Template(
        id_prod=1001, id_not_prod=136, tags=["demande_suspension_compte_jeune"], use_priority_queue=True
    )
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
    EXPIRED_BOOKING_TO_BENEFICIARY = models.Template(
        id_prod=145, id_not_prod=34, send_to_ehp=False, tags=["jeunes_resa_expiree"]
    )
    FRAUD_SUSPICION = models.Template(id_prod=82, id_not_prod=24, tags=["jeunes_compte_en_cours_d_analyse"])
    NEW_PASSWORD_REQUEST = models.Template(
        id_prod=141, id_not_prod=26, tags=["jeunes_nouveau_mdp"], use_priority_queue=True
    )
    NEW_PASSWORD_REQUEST_FOR_SUSPICIOUS_LOGIN = models.Template(
        id_prod=1108, id_not_prod=155, tags=["jeunes_nouveau_mdp_connexion_suspicieuse"], use_priority_queue=True
    )
    OFFER_WEBAPP_LINK_TO_IOS_USER = models.Template(
        id_prod=476, id_not_prod=45, tags=["redirect_ios"], use_priority_queue=True
    )
    OFFER_WITHDRAWAL_UPDATED_BY_PRO = models.Template(
        id_prod=868, id_not_prod=121, tags=["changement_modalites_retrait"]
    )
    PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY = models.Template(
        id_prod=510, id_not_prod=53, tags=["jeunes_erreur_importation_dms"]
    )
    RECREDIT_TO_UNDERAGE_BENEFICIARY = models.Template(
        id_prod=303, id_not_prod=31, tags=["anniversaire_16_17_ans"], send_to_ehp=False
    )
    REPORTED_OFFER_BY_USER = models.Template(id_prod=589, id_not_prod=70, tags=["interne_offre_signale"])
    SUBSCRIPTION_FOREIGN_DOCUMENT_ERROR = models.Template(
        id_prod=385, id_not_prod=40, tags=["jeunes_document_etranger"]
    )
    SUBSCRIPTION_INFORMATION_ERROR = models.Template(id_prod=410, id_not_prod=43, tags=["jeunes_infos_erronees"])
    SUBSCRIPTION_INVALID_DOCUMENT_ERROR = models.Template(
        id_prod=384, id_not_prod=39, tags=["jeunes_document_invalide"]
    )
    SUBSCRIPTION_NOT_AUTHENTIC_DOCUMENT_ERROR = models.Template(
        id_prod=760, id_not_prod=101, tags=["jeunes_document_non_authentique"]
    )
    SUBCRIPTION_REJECTED_FOR_DUPLICATE_BENEFICIARY = models.Template(
        id_prod=80, id_not_prod=77, tags=["jeunes_compte_refuse_doublon"]
    )
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

    # UBBLE KO REMINDER
    UBBLE_KO_REMINDER_ID_CHECK_DATA_MATCH = models.Template(id_prod=824, id_not_prod=116)
    UBBLE_KO_REMINDER_ID_CHECK_EXPIRED = models.Template(id_prod=831, id_not_prod=118)
    UBBLE_KO_REMINDER_ID_CHECK_NOT_AUTHENTIC = models.Template(id_prod=821, id_not_prod=117)
    UBBLE_KO_REMINDER_ID_CHECK_NOT_SUPPORTED = models.Template(id_prod=825, id_not_prod=119)
    UBBLE_KO_REMINDER_ID_CHECK_UNPROCESSABLE = models.Template(id_prod=823, id_not_prod=115)

    # PRO EMAIL
    BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO = models.TemplatePro(
        id_prod=379, id_not_prod=163, subaccount_id_prod=39, subaccount_id_not_prod=38
    )
    BOOKING_CANCELLATION_CONFIRMATION_BY_PRO = models.TemplatePro(
        id_prod=377, id_not_prod=60, subaccount_id_prod=40, subaccount_id_not_prod=39
    )
    BOOKING_EXPIRATION_TO_PRO = models.TemplatePro(
        id_prod=380, id_not_prod=50, subaccount_id_prod=38, subaccount_id_not_prod=37, send_to_ehp=False
    )
    EAC_NEW_BOOKING_TO_PRO = models.TemplatePro(
        id_prod=383, id_not_prod=67, subaccount_id_prod=18, subaccount_id_not_prod=18
    )
    EAC_NEW_PREBOOKING_TO_PRO = models.TemplatePro(
        id_prod=429, id_not_prod=68, subaccount_id_prod=19, subaccount_id_not_prod=19
    )
    EAC_ONE_DAY_AFTER_EVENT = models.TemplatePro(
        id_prod=523, id_not_prod=162, subaccount_id_prod=24, subaccount_id_not_prod=25
    )
    EAC_ONE_DAY_BEFORE_EVENT = models.TemplatePro(
        id_prod=615, id_not_prod=112, subaccount_id_prod=23, subaccount_id_not_prod=23
    )
    EAC_PENDING_BOOKING_WITH_BOOKING_LIMIT_DATE_3_DAYS = models.TemplatePro(
        id_prod=524, id_not_prod=64, subaccount_id_prod=22, subaccount_id_not_prod=22
    )
    EAC_NEW_REQUEST_FOR_OFFER = models.TemplatePro(
        id_prod=962, id_not_prod=128, subaccount_id_prod=54, subaccount_id_not_prod=41
    )
    EAC_OFFERER_ACTIVATION_EMAIL = models.TemplatePro(
        id_prod=815, id_not_prod=114, subaccount_id_prod=7, subaccount_id_not_prod=7, send_to_ehp=False
    )
    EDUCATIONAL_BOOKING_CANCELLATION = models.TemplatePro(
        id_prod=522, id_not_prod=65, subaccount_id_prod=17, subaccount_id_not_prod=17
    )
    EMAIL_VALIDATION_TO_PRO = models.TemplatePro(
        id_prod=361, id_not_prod=56, subaccount_id_prod=6, subaccount_id_not_prod=6
    )
    EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO = models.TemplatePro(
        id_prod=519, id_not_prod=63, subaccount_id_prod=37, subaccount_id_not_prod=36
    )
    PRO_EMAIL_CHANGE_CONFIRMATION = models.TemplatePro(
        id_prod=602, id_not_prod=100, subaccount_id_prod=14, subaccount_id_not_prod=14, use_priority_queue=True
    )
    PRO_EMAIL_CHANGE_REQUEST = models.TemplatePro(
        id_prod=601, id_not_prod=98, subaccount_id_prod=15, subaccount_id_not_prod=15, use_priority_queue=True
    )
    FIRST_VENUE_APPROVED_OFFER_TO_PRO = models.TemplatePro(
        id_prod=569, id_not_prod=75, subaccount_id_prod=4, subaccount_id_not_prod=4
    )
    FIRST_VENUE_BOOKING_TO_PRO = models.TemplatePro(
        id_prod=568, id_not_prod=78, subaccount_id_prod=20, subaccount_id_not_prod=20
    )
    INVOICE_AVAILABLE_TO_PRO = models.TemplatePro(
        id_prod=405, id_not_prod=95, subaccount_id_prod=27, subaccount_id_not_prod=27
    )
    NEW_BOOKING_TO_PRO = models.TemplatePro(
        id_prod=608, id_not_prod=59, subaccount_id_prod=21, subaccount_id_not_prod=21
    )
    NEW_OFFERER_VALIDATION = models.TemplatePro(
        id_prod=489, id_not_prod=58, subaccount_id_prod=3, subaccount_id_not_prod=3
    )
    NEW_OFFERER_REJECTION = models.TemplatePro(
        id_prod=790, id_not_prod=106, subaccount_id_prod=8, subaccount_id_not_prod=8
    )
    OFFER_APPROVAL_TO_PRO = models.TemplatePro(
        id_prod=349, id_not_prod=49, subaccount_id_prod=31, subaccount_id_not_prod=31
    )
    OFFERER_ATTACHMENT_INVITATION_NEW_USER = models.TemplatePro(
        id_prod=1045, id_not_prod=137, subaccount_id_prod=48, subaccount_id_not_prod=51
    )
    OFFERER_ATTACHMENT_INVITATION_EXISTING_VALIDATED_USER_EMAIL = models.TemplatePro(
        id_prod=1047, id_not_prod=143, subaccount_id_prod=46, subaccount_id_not_prod=49
    )
    OFFERER_ATTACHMENT_INVITATION_EXISTING_NOT_VALIDATED_USER_EMAIL = models.TemplatePro(
        id_prod=1046, id_not_prod=142, subaccount_id_prod=47, subaccount_id_not_prod=50
    )
    OFFERER_ATTACHMENT_INVITATION_ACCEPTED = models.TemplatePro(
        id_prod=1048, id_not_prod=138, subaccount_id_prod=45, subaccount_id_not_prod=48
    )
    OFFER_REJECTION_TO_PRO = models.TemplatePro(
        id_prod=375, id_not_prod=48, subaccount_id_prod=30, subaccount_id_not_prod=30
    )
    OFFER_PENDING_TO_REJECTED_TO_PRO = models.TemplatePro(
        id_prod=1026, id_not_prod=141, subaccount_id_prod=34, subaccount_id_not_prod=34
    )
    OFFER_VALIDATED_TO_REJECTED_TO_PRO = models.TemplatePro(
        id_prod=1023, id_not_prod=140, subaccount_id_prod=35, subaccount_id_not_prod=35
    )
    OFFERER_ATTACHMENT_VALIDATION = models.TemplatePro(
        id_prod=488, id_not_prod=62, subaccount_id_prod=2, subaccount_id_not_prod=2
    )
    OFFERER_ATTACHMENT_REJECTION = models.TemplatePro(
        id_prod=792, id_not_prod=107, subaccount_id_prod=9, subaccount_id_not_prod=9
    )
    REMINDER_OFFERER_INDIVIDUAL_SUBSCRIPTION = models.TemplatePro(
        id_prod=1295, id_not_prod=164, subaccount_id_prod=16, subaccount_id_not_prod=16
    )
    REMINDER_7_DAYS_BEFORE_EVENT_TO_PRO = models.TemplatePro(
        id_prod=587, id_not_prod=73, subaccount_id_prod=36, subaccount_id_not_prod=24
    )
    REMINDER_OFFER_CREATION_5_DAYS_AFTER_TO_PRO = models.TemplatePro(
        id_prod=566,
        id_not_prod=104,
        subaccount_id_prod=13,
        subaccount_id_not_prod=13,
        enable_unsubscribe=True,
    )
    REMINDER_OFFER_CREATION_10_DAYS_AFTER_TO_PRO = models.TemplatePro(
        id_prod=567,
        id_not_prod=105,
        subaccount_id_prod=12,
        subaccount_id_not_prod=12,
        enable_unsubscribe=True,
    )
    RESET_PASSWORD_TO_PRO = models.TemplatePro(
        id_prod=364, id_not_prod=47, subaccount_id_prod=5, subaccount_id_not_prod=5
    )
    RESET_PASSWORD_TO_CONNECTED_PRO = models.TemplatePro(
        id_prod=754, id_not_prod=99, subaccount_id_prod=11, subaccount_id_not_prod=11
    )
    WELCOME_TO_PRO = models.TemplatePro(id_prod=481, id_not_prod=57, subaccount_id_prod=1, subaccount_id_not_prod=1)
    VENUE_NEEDS_PICTURE = models.TemplatePro(
        id_prod=782, id_not_prod=113, subaccount_id_prod=10, subaccount_id_not_prod=10
    )
    VENUE_SYNC_DISABLED = models.TemplatePro(
        id_prod=883, id_not_prod=122, subaccount_id_prod=33, subaccount_id_not_prod=33
    )
    VENUE_SYNC_DELETED = models.TemplatePro(
        id_prod=865, id_not_prod=123, subaccount_id_prod=32, subaccount_id_not_prod=32
    )
    VENUE_BANK_ACCOUNT_LINK_DEPRECATED = models.TemplatePro(
        id_prod=1096, id_not_prod=148, subaccount_id_prod=29, subaccount_id_not_prod=29
    )
    BANK_ACCOUNT_VALIDATED = models.TemplatePro(
        id_prod=1095, id_not_prod=149, subaccount_id_prod=28, subaccount_id_not_prod=28
    )
    EXTERNAL_BOOKING_SUPPORT_CANCELLATION = models.TemplatePro(
        id_prod=1189, id_not_prod=158, subaccount_id_prod=26, subaccount_id_not_prod=26
    )

    # Finance incidents
    RETRIEVE_INCIDENT_AMOUNT_ON_INDIVIDUAL_BOOKINGS = models.TemplatePro(
        id_prod=1111, id_not_prod=150, subaccount_id_prod=77, subaccount_id_not_prod=54
    )
    RETRIEVE_INCIDENT_AMOUNT_ON_COLLECTIVE_BOOKINGS = models.TemplatePro(
        id_prod=1112, id_not_prod=151, subaccount_id_prod=78, subaccount_id_not_prod=55
    )
    RETRIEVE_DEBIT_NOTE_ON_INDIVIDUAL_BOOKINGS = models.TemplatePro(
        id_prod=0, id_not_prod=0, subaccount_id_prod=119, subaccount_id_not_prod=60
    )
    COMMERCIAL_GESTURE_REIMBURSEMENT = models.TemplatePro(
        id_prod=1187, id_not_prod=157, subaccount_id_prod=80, subaccount_id_not_prod=56
    )

    PROVIDER_REIMBURSEMENT_CSV = models.TemplatePro(
        id_prod=1392, id_not_prod=167, subaccount_id_prod=81, subaccount_id_not_prod=57
    )
