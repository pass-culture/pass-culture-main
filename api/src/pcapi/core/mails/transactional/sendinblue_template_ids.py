import dataclasses
from enum import Enum

from pcapi import settings


@dataclasses.dataclass
class Template:
    id_prod: int
    id_not_prod: int
    tags: list[str] = dataclasses.field(default_factory=list)
    use_priority_queue: bool = False
    # Tag your emails to find them more easily cf doc https://developers.sendinblue.com/reference/sendtransacemail

    @property
    def id(self) -> int:
        return self.id_prod if settings.IS_PROD else self.id_not_prod


class TransactionalEmail(Enum):
    ACCEPTED_AS_BENEFICIARY = Template(
        id_prod=96, id_not_prod=25, tags=["jeunes_pass_credite_18"], use_priority_queue=True
    )
    ACCEPTED_AS_EAC_BENEFICIARY = Template(
        id_prod=257, id_not_prod=27, tags=["jeunes_pass_credite_eac"], use_priority_queue=True
    )
    BOOKING_CANCELLATION_BY_BENEFICIARY = Template(id_prod=223, id_not_prod=33, tags=["jeunes_offre_annulee_jeune"])
    BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY = Template(
        id_prod=225, id_not_prod=37, tags=["jeunes_offre_annulee_pros"]
    )
    BOOKING_CONFIRMATION_BY_BENEFICIARY = Template(id_prod=219, id_not_prod=29, tags=["jeunes_reservation_confirmee"])
    BOOKING_POSTPONED_BY_PRO_TO_BENEFICIARY = Template(id_prod=224, id_not_prod=36, tags=["jeunes_offre_reportee_pro"])
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
    EXPIRED_BOOKINGS_TO_BENEFICIARY = Template(id_prod=145, id_not_prod=34, tags=["jeunes_resa_expiree"])
    FRAUD_SUSPICION = Template(id_prod=82, id_not_prod=24, tags=["jeunes_compte_en_cours_d_analyse"])
    NEW_PASSWORD_REQUEST = Template(id_prod=141, id_not_prod=26, tags=["jeunes_nouveau_mdp"], use_priority_queue=True)
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


@dataclasses.dataclass
class SendinblueTransactionalEmailData:
    template: Template
    params: dict = dataclasses.field(default_factory=dict)
