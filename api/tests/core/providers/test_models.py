import pytest

from pcapi.core.providers import factories
from pcapi.core.providers import models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def test_isFromAllocineProvider():
    allocine = factories.AllocineProviderFactory()
    allocine_venue_provider = factories.VenueProviderFactory(provider=allocine)
    assert allocine_venue_provider.isFromAllocineProvider

    other = factories.ProviderFactory(localClass="Dummy")
    other_venue_provider = factories.VenueProviderFactory(provider=other)
    assert not other_venue_provider.isFromAllocineProvider


def test_boost_cinema_details_unencrypted_token():
    unencrypted_secret = "fake.jwtLike.format"
    boost = factories.BoostCinemaDetailsFactory()
    boost_id = boost.id
    db.session.query(models.BoostCinemaDetails).filter(models.BoostCinemaDetails.id == boost_id).update(
        {"_token": unencrypted_secret}
    )

    db.session.expunge(boost)
    assert (
        db.session.query(models.BoostCinemaDetails).filter(models.BoostCinemaDetails.id == boost_id).one().token
        == unencrypted_secret
    )


def test_CDS_cinema_details_unencrypted_token():
    unencrypted_secret = "LOOKS-LIKE-A-UUID"
    CDS = factories.CDSCinemaDetailsFactory()
    cds_id = CDS.id
    db.session.query(models.CDSCinemaDetails).filter(models.CDSCinemaDetails.id == cds_id).update(
        {"_cinemaApiToken": unencrypted_secret}
    )

    db.session.expunge(CDS)
    assert (
        db.session.query(models.CDSCinemaDetails).filter(models.CDSCinemaDetails.id == cds_id).one().cinemaApiToken
        == unencrypted_secret
    )
