import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.educational import factories as educational_factories
from pcapi.models import db
from pcapi.scripts.assign_activity_to_venues.main import main


pytestmark = pytest.mark.usefixtures("db_session")


def test_assign_activity():
    domains = [
        educational_factories.EducationalDomainFactory.create(
            name="Univers du livre, de la lecture et des écritures",
        ),
        educational_factories.EducationalDomainFactory.create(name="Bande dessinée"),
    ]
    offerer = offerers_factories.OffererFactory()
    venue_null = offerers_factories.VenueFactory(managingOfferer=offerer, activity=None, isOpenToPublic=True)
    venue_not_assigned = offerers_factories.VenueFactory(
        managingOfferer=offerer,
        activity=offerers_models.Activity.NOT_ASSIGNED,
        isOpenToPublic=True,
        collectiveDomains=[domains[0]],
    )
    venue_other = offerers_factories.VenueFactory(
        managingOfferer=offerer, activity=offerers_models.Activity.OTHER, isOpenToPublic=True
    )
    venue_unrelated = offerers_factories.VenueFactory(
        managingOfferer=offerer, activity=offerers_models.Activity.NOT_ASSIGNED, isOpenToPublic=True
    )

    data = [
        {"venue_id": venue_null.id, "new_category": "Librairie"},
        {"venue_id": venue_other.id, "new_category": "Librairie"},
        {"venue_id": venue_not_assigned.id, "new_category": "Librairie"},
        {"venue_id": venue_unrelated.id, "new_category": "Cinéma"},
    ]

    assert venue_null.collectiveDomains == []
    assert venue_not_assigned.collectiveDomains == [domains[0]]
    assert venue_other.collectiveDomains == []
    assert venue_unrelated.collectiveDomains == []

    main(data, activity=offerers_models.Activity.BOOKSTORE)

    db.session.expire_all()
    assert venue_null.activity == offerers_models.Activity.BOOKSTORE
    assert venue_not_assigned.activity == offerers_models.Activity.BOOKSTORE
    assert venue_other.activity == offerers_models.Activity.OTHER
    assert venue_unrelated.activity == offerers_models.Activity.NOT_ASSIGNED

    assert set(venue_null.collectiveDomains) == set(domains)
    assert set(venue_not_assigned.collectiveDomains) == set(domains)
    assert venue_other.collectiveDomains == []
    assert venue_unrelated.collectiveDomains == []
