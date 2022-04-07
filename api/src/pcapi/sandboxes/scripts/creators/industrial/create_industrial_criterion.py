import logging

from pcapi.models.criterion import Criterion
from pcapi.models.offer_criterion import OfferCriterion
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def create_industrial_criteria() -> dict:
    logger.info("create_industrial_criteria")

    criteria_by_name = {}

    criterion1 = Criterion()
    criterion1.name = "Bonne offre d’appel"
    criterion1.description = "Offre déjà beaucoup réservée par les autres jeunes"
    criteria_by_name[criterion1.name] = criterion1

    criterion2 = Criterion()
    criterion2.name = "Mauvaise accroche"
    criterion2.description = "Offre ne possédant pas une accroche de qualité suffisante"
    criteria_by_name[criterion2.name] = criterion2

    criterion3 = Criterion()
    criterion3.name = "Offre de médiation spécifique"
    criterion3.description = "Offre possédant une médiation orientée pour les jeunes de 18 ans"
    criteria_by_name[criterion3.name] = criterion3

    repository.save(*criteria_by_name.values())

    logger.info("created %d criteria", len(criteria_by_name))

    return criteria_by_name


def associate_criterion_to_one_offer_with_mediation(offers_by_name: dict, criteria_by_name: dict):  # type: ignore [no-untyped-def]
    offer = list(filter(lambda o: o.mediations is not None, list(offers_by_name.values())))[0]
    criterion = criteria_by_name["Offre de médiation spécifique"]

    offer_criterion = OfferCriterion()
    offer_criterion.offer = offer
    offer_criterion.criterion = criterion

    repository.save(offer_criterion)
