from enum import Enum

from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalSender
from pcapi.core.mails.models.sendinblue_models import Template
from pcapi.core.mails.models.sendinblue_models import TemplatePro


class TransactionalEmail(Enum):
    ACCEPTED_AS_BENEFICIARY = Template(
        id_prod=96, id_not_prod=25, tags=["jeunes_pass_credite_18"], use_priority_queue=True
    )
    ACCEPTED_AS_EAC_BENEFICIARY = Template(
        id_prod=257, id_not_prod=27, tags=["jeunes_pass_credite_eac"], use_priority_queue=True
    )
    BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER = Template(id_prod=78, id_not_prod=32, tags=["anniversaire_18_ans"])
    BOOKING_CANCELLATION_BY_BENEFICIARY = Template(id_prod=223, id_not_prod=33, tags=["jeunes_offre_annulee_jeune"])
    BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY = Template(
        id_prod=225, id_not_prod=37, tags=["jeunes_offre_annulee_pros"]
    )
    BOOKING_CONFIRMATION_BY_BENEFICIARY = Template(id_prod=219, id_not_prod=29, tags=["jeunes_reservation_confirmee"])
    BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY = Template(id_prod=224, id_not_prod=36, tags=["jeunes_offre_reportee_pro"])
    BOOKING_SOON_TO_BE_EXPIRED_TO_BENEFICIARY = Template(
        id_prod=144, id_not_prod=42, tags=["jeunes_reservation_bientot_expiree"]
    )
    EDUCATIONAL_BOOKING_CANCELLATION_BY_INSTITUTION = Template(
        id_prod=406, id_not_prod=41, tags=["eac_annulationoffre"]
    )
    EMAIL_CHANGE_CONFIRMATION = Template(
        id_prod=253, id_not_prod=18, tags=["changement_email_confirmation"], use_priority_queue=True
    )
    EMAIL_CHANGE_REQUEST = Template(
        id_prod=142, id_not_prod=17, tags=["changement_email_demande"], use_priority_queue=True
    )
    EMAIL_CONFIRMATION = Template(
        id_prod=201, id_not_prod=15, tags=["jeunes_confirmation_mail"], use_priority_queue=True
    )
    EMAIL_DUPLICATE_BENEFICIARY_PRE_SUBCRIPTION_REJECTED = Template(
        id_prod=80, id_not_prod=19, tags=["jeunes_compte_refuse_doublon"], use_priority_queue=True
    )

    EXPIRED_BOOKING_TO_BENEFICIARY = Template(id_prod=145, id_not_prod=34, tags=["jeunes_resa_expiree"])
    FRAUD_SUSPICION = Template(id_prod=82, id_not_prod=24, tags=["jeunes_compte_en_cours_d_analyse"])
    NEW_PASSWORD_REQUEST = Template(id_prod=141, id_not_prod=26, tags=["jeunes_nouveau_mdp"], use_priority_queue=True)
    OFFER_WEBAPP_LINK_TO_IOS_USER = Template(
        id_prod=476, id_not_prod=45, tags=["redirect_ios"], use_priority_queue=True
    )
    PRE_SUBSCRIPTION_DMS_ERROR_TO_BENEFICIARY = Template(
        id_prod=510, id_not_prod=53, tags=["jeunes_erreur_importation_dms"]
    )
    RECREDIT_TO_UNDERAGE_BENEFICIARY = Template(id_prod=303, id_not_prod=31, tags=["anniversaire_16_17_ans"])
    SUBSCRIPTION_FOREIGN_DOCUMENT_ERROR = Template(
        id_prod=385,
        id_not_prod=40,
        tags=["jeunes_document_etranger"],
        use_priority_queue=True,
    )
    SUBSCRIPTION_INFORMATION_ERROR = Template(
        id_prod=410,
        id_not_prod=43,
        tags=["jeunes_infos_erronees"],
        use_priority_queue=True,
    )
    SUBSCRIPTION_INVALID_DOCUMENT_ERROR = Template(
        id_prod=384,
        id_not_prod=39,
        tags=["jeunes_document_invalide"],
        use_priority_queue=True,
    )
    SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR = Template(
        id_prod=304,
        id_not_prod=38,
        tags=["jeunes_document_illisible"],
        use_priority_queue=True,
    )
    USER_REQUEST_DELETE_ACCOUNT_RECEPTION = Template(
        id_prod=511, id_not_prod=54, tags=["reception_demande_suppression_compte_jeune"]
    )

    # PRO EMAIL
    EMAIL_VALIDATION_TO_PRO = TemplatePro(id_prod=361, id_not_prod=56, tags=["validation_email_invitation_pro"])
    BOOKING_CANCELLATION_BY_BENEFICIARY_TO_PRO = TemplatePro(id_prod=379, id_not_prod=51, tags=["pro_annulation_offre"])
    BOOKING_CANCELLATION_CONFIRMATION_BY_PRO = TemplatePro(
        id_prod=377, id_not_prod=60, tags=["pro_annulation_rerservation"]
    )
    BOOKING_EXPIRATION_TO_PRO = TemplatePro(id_prod=380, id_not_prod=50, tags=["pro_reservation_expiree_30j"])
    EAC_BOOKING_DAY_TO_PRO = TemplatePro(id_prod=0000, id_not_prod=0000, tags=[""])
    EAC_NEW_BOOKING_TO_PRO = TemplatePro(id_prod=0000, id_not_prod=0000, tags=["pro_nouvelle_reservation_eac"])
    EAC_NEW_PREBOOKING_TO_PRO = TemplatePro(id_prod=0000, id_not_prod=0000, tags=["pro_nouvelle_prereservation_eac"])
    EAC_SATISFACTION_STUDY_TO_PRO = TemplatePro(id_prod=0000, id_not_prod=0000, tags=[""])
    EXCEEDING_20K_REVENUE_TO_PRO = TemplatePro(id_prod=0000, id_not_prod=0000, tags=["pro_depassement_20k"])
    FIRST_BOOKING_TO_PRO = TemplatePro(id_prod=0000, id_not_prod=0000, tags=[""])
    FIRST_OFFER_CREATED_BY_PRO = TemplatePro(id_prod=0000, id_not_prod=0000, tags=[""])
    FRAUD_PREVENTION_TO_PRO = TemplatePro(id_prod=0000, id_not_prod=0000, tags=[""])
    INVOICE_AVAILABLE_TO_PRO = TemplatePro(id_prod=405, id_not_prod=61, tags=["remboursement_justificatif"])
    NEW_BOOKING_TO_PRO = TemplatePro(id_prod=376, id_not_prod=59, tags=["pro_nouvelle_reservation"])
    OFFER_APPROVAL_TO_PRO = TemplatePro(
        id_prod=349, id_not_prod=49, tags=["pro_validation_offre"], sender=SendinblueTransactionalSender.COMPLIANCE
    )
    OFFER_REJECTION_TO_PRO = TemplatePro(
        id_prod=375, id_not_prod=48, tags=["pro_offre_refusee"], sender=SendinblueTransactionalSender.COMPLIANCE
    )
    REFUND_TO_PRO = TemplatePro(id_prod=0000, id_not_prod=0000, tags=[""])
    RESET_PASSWORD_TO_PRO = TemplatePro(id_prod=364, id_not_prod=47, tags=["pro_reinit_mdp"])
    WELCOME_TO_PRO = TemplatePro(id_prod=481, id_not_prod=57, tags=["pro-bienvenue-pass"])
