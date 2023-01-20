from enum import Enum

from pcapi.core.mails import models


class TransactionalEmail(Enum):
    ACCEPTED_AS_BENEFICIARY = models.Template(
        id_prod=96, id_not_prod=25, tags=["jeunes_pass_credite_18"], use_priority_queue=True
    )
    ACCEPTED_AS_EAC_BENEFICIARY = models.Template(
        id_prod=257, id_not_prod=27, tags=["jeunes_pass_credite_eac"], use_priority_queue=True
    )
    ACCOUNT_UNSUSPENDED = models.Template(id_prod=644, id_not_prod=87, tags=["reactivation_compte_utilisateur"])
    BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER = models.Template(
        id_prod=78, id_not_prod=32, tags=["anniversaire_18_ans"], send_to_ehp=False
    )
    BOOKING_CANCELLATION_BY_BENEFICIARY = models.Template(
        id_prod=223, id_not_prod=33, tags=["jeunes_offre_annulee_jeune"]
    )
    BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY = models.Template(
        id_prod=225, id_not_prod=37, tags=["jeunes_offre_annulee_pros"]
    )
    BOOKING_CONFIRMATION_BY_BENEFICIARY = models.Template(
        id_prod=725, id_not_prod=96, tags=["jeunes_reservation_confirmee_v3"]
    )
    BOOKING_EVENT_REMINDER_TO_BENEFICIARY = models.Template(
        id_prod=665, id_not_prod=82, tags=["jeunes_rappel_evenement_j-1"]
    )
    BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY = models.Template(
        id_prod=224, id_not_prod=36, tags=["jeunes_offre_reportee_pro"]
    )
    BOOKING_SOON_TO_BE_EXPIRED_TO_BENEFICIARY = models.Template(
        id_prod=144, id_not_prod=42, tags=["jeunes_reservation_bientot_expiree"]
    )
    COMPLETE_SUBSCRIPTION_AFTER_DMS = models.Template(
        id_prod=679, id_not_prod=84, tags=["jeunes_complete_inscription_apres_dms"]
    )
    CREATE_ACCOUNT_AFTER_DMS = models.Template(id_prod=678, id_not_prod=85, tags=["jeunes_creation_compte_apres_dms"])
    EMAIL_ALREADY_EXISTS = models.Template(id_prod=617, id_not_prod=79, tags=["email_existant_en_base"])
    EMAIL_CHANGE_CONFIRMATION = models.Template(
        id_prod=253, id_not_prod=18, tags=["changement_email_confirmation"], use_priority_queue=True
    )
    EMAIL_CHANGE_REQUEST = models.Template(
        id_prod=142, id_not_prod=17, tags=["changement_email_demande"], use_priority_queue=True
    )
    EMAIL_CONFIRMATION = models.Template(
        id_prod=201, id_not_prod=15, tags=["jeunes_confirmation_mail"], use_priority_queue=True
    )
    EXPIRED_BOOKING_TO_BENEFICIARY = models.Template(id_prod=145, id_not_prod=34, tags=["jeunes_resa_expiree"])
    FRAUD_SUSPICION = models.Template(id_prod=82, id_not_prod=24, tags=["jeunes_compte_en_cours_d_analyse"])
    NEW_PASSWORD_REQUEST = models.Template(
        id_prod=141, id_not_prod=26, tags=["jeunes_nouveau_mdp"], use_priority_queue=True
    )
    OFFER_WEBAPP_LINK_TO_IOS_USER = models.Template(
        id_prod=476, id_not_prod=45, tags=["redirect_ios"], use_priority_queue=True
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
    USER_REQUEST_DELETE_ACCOUNT_RECEPTION = models.Template(
        id_prod=511, id_not_prod=54, tags=["reception_demande_suppression_compte_jeune"]
    )

    # UBBLE KO REMINDER
    UBBLE_KO_REMINDER_ID_CHECK_DATA_MATCH = models.Template(
        id_prod=824, id_not_prod=116, tags=["jeunes_relance_ubble_ko_infos_incorrectes"]
    )
    UBBLE_KO_REMINDER_ID_CHECK_EXPIRED = models.Template(
        id_prod=831, id_not_prod=118, tags=["jeunes_relance_ubble_ko_document_expire"]
    )
    UBBLE_KO_REMINDER_ID_CHECK_NOT_AUTHENTIC = models.Template(
        id_prod=821, id_not_prod=117, tags=["jeunes_relance_ubble_ko_document_non_authentique"]
    )
    UBBLE_KO_REMINDER_ID_CHECK_NOT_SUPPORTED = models.Template(
        id_prod=825, id_not_prod=119, tags=["jeunes_relance_ubble_ko_document_non_supporte"]
    )
    UBBLE_KO_REMINDER_ID_CHECK_UNPROCESSABLE = models.Template(
        id_prod=823, id_not_prod=115, tags=["jeunes_relance_ubble_ko_video_illisible"]
    )

    # PRO EMAIL

    BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO = models.TemplatePro(
        id_prod=609, id_not_prod=51, tags=["pro_annulation_offre"]
    )
    BOOKING_CANCELLATION_CONFIRMATION_BY_PRO = models.TemplatePro(
        id_prod=377, id_not_prod=60, tags=["pro_annulation_rerservation"]
    )
    BOOKING_EXPIRATION_TO_PRO = models.TemplatePro(id_prod=380, id_not_prod=50, tags=["pro_reservation_expiree_30j"])
    EAC_NEW_BOOKING_TO_PRO = models.TemplatePro(id_prod=383, id_not_prod=67, tags=["pro_nouvelle_reservation_eac"])
    EAC_NEW_PREBOOKING_TO_PRO = models.TemplatePro(
        id_prod=429, id_not_prod=68, tags=["pro_nouvelle_prereservation_eac"]
    )
    EAC_ONE_DAY_BEFORE_EVENT = models.TemplatePro(id_prod=615, id_not_prod=112, tags=["pro_notification_1j"])
    EAC_PENDING_BOOKING_WITH_BOOKING_LIMIT_DATE_3_DAYS = models.TemplatePro(
        id_prod=524, id_not_prod=64, tags=["pro_preresa_3_jours_avant_la_date_limite"]
    )
    EAC_OFFERER_ACTIVATION_EMAIL = models.TemplatePro(id_prod=815, id_not_prod=114, tags=["pro_offerer_activation"])
    EDUCATIONAL_BOOKING_CANCELLATION = models.TemplatePro(
        id_prod=522, id_not_prod=65, tags=["pro_eac_annulation_reservation"]
    )
    EMAIL_VALIDATION_TO_PRO = models.TemplatePro(id_prod=361, id_not_prod=56, tags=["validation_email_invitation_pro"])
    EVENT_OFFER_POSTPONED_CONFIRMATION_TO_PRO = models.TemplatePro(
        id_prod=519, id_not_prod=63, tags=["pro_offre_evenement_reportee"]
    )
    PRO_EMAIL_CHANGE_CONFIRMATION = models.Template(
        id_prod=602, id_not_prod=100, tags=["pro_changement_email_confirmation"], use_priority_queue=True
    )
    PRO_EMAIL_CHANGE_REQUEST = models.Template(
        id_prod=601, id_not_prod=98, tags=["pro_changement_email_demande"], use_priority_queue=True
    )
    FIRST_VENUE_APPROVED_OFFER_TO_PRO = models.TemplatePro(id_prod=569, id_not_prod=75, tags=["pro_premiere_offre"])
    FIRST_VENUE_BOOKING_TO_PRO = models.TemplatePro(id_prod=568, id_not_prod=78, tags=["pro_premiere_reservation"])
    INVOICE_AVAILABLE_TO_PRO = models.TemplatePro(id_prod=405, id_not_prod=95, tags=["remboursement_justificatif"])
    NEW_BOOKING_TO_PRO = models.TemplatePro(id_prod=608, id_not_prod=59, tags=["pro_nouvelle_reservation"])
    NEW_OFFERER_VALIDATION = models.TemplatePro(id_prod=489, id_not_prod=58, tags=["pro_validation_structure"])
    NEW_OFFERER_REJECTION = models.TemplatePro(id_prod=790, id_not_prod=106, tags=["pro_rejet_structure"])
    OFFER_APPROVAL_TO_PRO = models.TemplatePro(
        id_prod=349,
        id_not_prod=49,
        tags=["pro_validation_offre"],
        sender=models.TransactionalSender.COMPLIANCE,
    )
    OFFER_REJECTION_TO_PRO = models.TemplatePro(
        id_prod=375,
        id_not_prod=48,
        tags=["pro_offre_refusee"],
        sender=models.TransactionalSender.COMPLIANCE,
    )
    OFFERER_ATTACHMENT_VALIDATION = models.TemplatePro(
        id_prod=488, id_not_prod=62, tags=["pro_rattachement_structure_valide"]
    )
    OFFERER_ATTACHMENT_REJECTION = models.TemplatePro(
        id_prod=792, id_not_prod=107, tags=["pro_rattachement_structure_rejet"]
    )
    REMINDER_7_DAYS_BEFORE_EVENT_TO_PRO = models.TemplatePro(id_prod=587, id_not_prod=73, tags=["pro_rappel_event_J-7"])
    REMINDER_OFFER_CREATION_5_DAYS_AFTER_TO_PRO = models.TemplatePro(
        id_prod=566, id_not_prod=104, tags=["pro_relance_offre_J+5"]
    )
    REMINDER_OFFER_CREATION_10_DAYS_AFTER_TO_PRO = models.TemplatePro(
        id_prod=567, id_not_prod=105, tags=["pro_relance_offre_J+10"]
    )
    REMINDER_VENUE_CREATION_TO_PRO = models.TemplatePro(id_prod=571, id_not_prod=97, tags=["pro_relance_lieu"])
    RESET_PASSWORD_TO_PRO = models.TemplatePro(id_prod=364, id_not_prod=47, tags=["pro_reinit_mdp"])
    RESET_PASSWORD_TO_CONNECTED_PRO = models.TemplatePro(
        id_prod=754, id_not_prod=99, tags=["pro_reinit_mdp_when_connected"]
    )
    WELCOME_TO_PRO = models.TemplatePro(id_prod=481, id_not_prod=57, tags=["pro-bienvenue-pass"])
    VENUE_NEEDS_PICTURE = models.TemplatePro(id_prod=782, id_not_prod=113, tags=["pro_lieu_permanent"])
    VENUE_SYNC_DISABLED = models.TemplatePro(id_prod=883, id_not_prod=122, tags=["pro_pause_synchro"])
    VENUE_SYNC_DELETED = models.TemplatePro(id_prod=865, id_not_prod=123, tags=["pro_suppression_synchro"])
