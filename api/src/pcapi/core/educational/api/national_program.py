from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.models import db
from pcapi.repository import repository


AnyCollectiveOffer = models.CollectiveOffer | models.CollectiveOfferTemplate


def create_national_program(name: str) -> models.NationalProgram:
    program = models.NationalProgram(name=name)
    repository.save(program)
    return program


def link_collective_offer_to_program(
    program: models.NationalProgram, offer: AnyCollectiveOffer, commit: bool = True
) -> None:
    offer.nationalProgramId = program.id

    if isinstance(offer, models.CollectiveOffer):
        history_event = models.NationalProgramOfferLinkHistory(nationalProgramId=program.id, collectiveOfferId=offer.id)
    else:
        history_event = models.NationalProgramOfferTemplateLinkHistory(
            nationalProgramId=program.id, collectiveOfferTemplateId=offer.id
        )

    if commit:
        repository.save(offer, history_event)
    else:
        db.session.add_all([offer, history_event])


def link_offer_to_program(program_id: int, offer: AnyCollectiveOffer, commit: bool = True) -> None:
    program = models.NationalProgram.query.get(program_id)
    if not program:
        raise exceptions.NationalProgramNotFound()

    link_collective_offer_to_program(program, offer, commit)
