import pytest

from pcapi.core.criteria.factories import CriterionFactory
from pcapi.core.educational.factories import EducationalDomainFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offerers.models import Activity


pytestmark = pytest.mark.usefixtures("db_session")


def test_set_specific_cases(db_session):
    microfolie_criterion = CriterionFactory(name="Microfolie")
    science_centre_criterion = CriterionFactory(name="Culture scientifique")
    domain_patrimoine = EducationalDomainFactory(name="Patrimoine")

    venue0 = VenueFactory(  # not affected
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
        managingOfferer__isActive=True,
    )
    venue1 = VenueFactory(  # REJECTED
        isOpenToPublic=True,
        venueTypeCode="OTHER",
        activity=None,
        managingOfferer__validationStatus="REJECTED",
        managingOfferer__isActive=True,
    )
    venue2 = VenueFactory(  # REJECTED + criterion Microfolie
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
        managingOfferer__validationStatus="REJECTED",
        managingOfferer__isActive=True,
    )
    venue2.criteria.append(microfolie_criterion)
    venue3 = VenueFactory(  # criterion Microfolie
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
        managingOfferer__isActive=True,
    )
    venue3.criteria.append(microfolie_criterion)
    venue4 = VenueFactory(  # criterion microfolie takes precedence
        isOpenToPublic=True,
        venueTypeCode="OTHER",
        activity=None,
        managingOfferer__isActive=True,
    )
    venue4.criteria.append(microfolie_criterion)
    venue4.criteria.append(science_centre_criterion)
    venue5 = VenueFactory(  # criterion science centre
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
        managingOfferer__isActive=True,
    )
    venue5.criteria.append(science_centre_criterion)
    venue6 = VenueFactory(
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
        managingOfferer__isActive=True,
    )
    venue6.collectiveDomains.append(domain_patrimoine)
    venue7 = VenueFactory(  # inactive
        isOpenToPublic=True,
        venueTypeCode="DIGITAL",
        activity=None,
        managingOfferer__isActive=False,
    )

    from pcapi.scripts.set_venue_activity_specific_cases.main import set_specific_cases

    set_specific_cases(not_dry=True)

    assert venue0.activity == None
    assert venue1.activity == Activity.OTHER
    assert venue2.activity == Activity.OTHER  # REJECTED takes precedence
    assert venue3.activity == Activity.MUSEUM
    assert venue4.activity == Activity.MUSEUM
    assert venue5.activity == Activity.SCIENCE_CENTRE
    assert venue6.activity == Activity.HERITAGE_SITE
    assert venue7.activity == Activity.OTHER
