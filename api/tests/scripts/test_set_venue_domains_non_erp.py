import pytest

from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
from pcapi.core.educational.factories import EducationalDomainFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.models import offer_mixin


pytestmark = pytest.mark.usefixtures("db_session")


def test_fetch_only_relevant_domains():
    music = EducationalDomainFactory(name="MUSIC")
    theater = EducationalDomainFactory(name="THEATER")
    dance = EducationalDomainFactory(name="DANCE")
    circus = EducationalDomainFactory(name="CIRCUS")
    crochet = EducationalDomainFactory(name="CROCHET")
    animals = EducationalDomainFactory(name="ANIMALS")
    relevant_venue = VenueFactory(
        isOpenToPublic=False,
        collectiveDomains=[],
    )
    non_relevant_venue = VenueFactory(
        isOpenToPublic=True,
        collectiveDomains=[],
    )
    non_relevant_venue_bis = VenueFactory(
        isOpenToPublic=False,
        collectiveDomains=[music],
    )
    unfitoffers_venue = VenueFactory(
        isOpenToPublic=False,
        collectiveDomains=[],
    )
    CollectiveOfferFactory(
        venue=relevant_venue,
        validation=offer_mixin.OfferValidationStatus.APPROVED,
        educational_domains=[music, theater],
    )
    CollectiveOfferFactory(
        venue=relevant_venue,
        validation=offer_mixin.OfferValidationStatus.REJECTED,
        educational_domains=[dance],
    )
    CollectiveOfferTemplateFactory(
        venue=relevant_venue,
        validation=offer_mixin.OfferValidationStatus.APPROVED,
        educational_domains=[circus],
    )
    CollectiveOfferTemplateFactory(
        venue=relevant_venue,
        validation=offer_mixin.OfferValidationStatus.PENDING,
        educational_domains=[animals],
    )
    CollectiveOfferFactory(
        venue=unfitoffers_venue,
        validation=offer_mixin.OfferValidationStatus.DRAFT,
        educational_domains=[circus],
    )
    CollectiveOfferFactory(
        venue=unfitoffers_venue,
        validation=offer_mixin.OfferValidationStatus.APPROVED,
        educational_domains=[crochet],
    )
    CollectiveOfferFactory(
        venue=non_relevant_venue,
        validation=offer_mixin.OfferValidationStatus.APPROVED,
        educational_domains=[animals],
    )
    CollectiveOfferTemplateFactory(
        venue=non_relevant_venue_bis,
        validation=offer_mixin.OfferValidationStatus.APPROVED,
        educational_domains=[animals],
    )

    from pcapi.scripts.set_venue_domain_non_erp.main import main

    main(not_dry=True)

    assert relevant_venue.collectiveDomains == [music, theater, circus]
    assert non_relevant_venue.collectiveDomains == []
    assert unfitoffers_venue.collectiveDomains == [crochet]
    assert non_relevant_venue_bis.collectiveDomains == [music]
