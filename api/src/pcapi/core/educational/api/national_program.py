from pcapi.core.educational import exceptions
from pcapi.core.educational import models
from pcapi.models import db
from pcapi.repository import repository


AnyCollectiveOffer = models.CollectiveOffer | models.CollectiveOfferTemplate


def _link_offer(program: models.NationalProgram, offer: AnyCollectiveOffer, commit: bool) -> None:
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


def _unlink_offer(offer: AnyCollectiveOffer, commit: bool) -> None:
    offer.nationalProgramId = None

    if commit:
        repository.save(offer)
    else:
        db.session.add(offer)


def link_or_unlink_offer_to_program(program_id: int | None, offer: AnyCollectiveOffer, commit: bool = True) -> None:
    """
    Link offer to national program and save this change within the
    offer's national programs history.

    Unlink the offer if program_id is None.
    """
    if not program_id:
        _unlink_offer(offer, commit)
        return

    program = get_national_program(program_id)
    if not program:
        raise exceptions.NationalProgramNotFound()

    _link_offer(program, offer, commit)


def get_national_program(program_id: int | None) -> models.NationalProgram | None:
    if not program_id:
        return None

    return models.NationalProgram.query.get(program_id)
