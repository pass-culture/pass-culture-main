import pytest

from pcapi.core.criteria.factories import CriterionFactory
from pcapi.core.educational.factories import EducationalDomainFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.models import Activity
from pcapi.core.offers.factories import OfferFactory
from pcapi.scripts.set_venue_activity_tourist_information_centre.main import set_specific_cases


pytestmark = pytest.mark.usefixtures("db_session")


def test_set_specific_cases(db_session):
    microfolie_criterion = CriterionFactory(name="Microfolie")
    science_centre_criterion = CriterionFactory(name="Culture scientifique")
    domain_patrimoine = EducationalDomainFactory(name="Patrimoine")

    venue0 = VenueFactory(  # not affected
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
    )
    venue1 = VenueFactory(  # REJECTED
        isOpenToPublic=True,
        venueTypeCode="OTHER",
        activity=None,
        managingOfferer__validationStatus="REJECTED",
    )
    venue2 = VenueFactory(  # REJECTED + criterion Microfolie
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
        managingOfferer__validationStatus="REJECTED",
    )
    venue2.criteria.append(microfolie_criterion)
    venue3 = VenueFactory(  # criterion Microfolie
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
    )
    venue3.criteria.append(microfolie_criterion)
    venue4 = VenueFactory(  # criterion microfolie takes precedence
        isOpenToPublic=True,
        venueTypeCode="OTHER",
        activity=None,
    )
    venue4.criteria.append(microfolie_criterion)
    venue4.criteria.append(science_centre_criterion)
    venue5 = VenueFactory(  # criterion science centre
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
    )
    venue5.criteria.append(science_centre_criterion)
    venue6 = VenueFactory(
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
    )
    venue6.collectiveDomains.append(domain_patrimoine)
    venue7 = VenueFactory(
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
    )
    venue8 = VenueFactory(
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
    )
    OfferFactory(venue=venue7, subcategoryId="SEANCE_CINE")
    OfferFactory(venue=venue8, subcategoryId="SPECTACLE_REPRESENTATION")

    set_specific_cases(not_dry=True)

    assert venue0.activity == None
    assert venue1.activity == Activity.OTHER
    assert venue2.activity == Activity.OTHER  # REJECTED takes precedence
    assert venue3.activity == Activity.MUSEUM
    assert venue4.activity == Activity.MUSEUM
    assert venue5.activity == Activity.SCIENCE_CENTRE
    assert venue6.activity == Activity.HERITAGE_SITE
    assert venue7.activity == Activity.CINEMA
    assert venue8.activity == Activity.PERFORMANCE_HALL
