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
    db_boost = db.session.query(models.BoostCinemaDetails).filter(models.BoostCinemaDetails.id == boost_id).one()
    assert db_boost.token == unencrypted_secret


def test_boost_cinema_details_update_token():
    unencrypted_secret = "fake.jwtLike.format"
    boost = factories.BoostCinemaDetailsFactory()
    boost_id = boost.id

    boost.token = unencrypted_secret
    db.session.commit()

    db.session.expunge(boost)
    db_boost = db.session.query(models.BoostCinemaDetails).filter(models.BoostCinemaDetails.id == boost_id).one()
    assert db_boost.token == unencrypted_secret


def test_CDS_cinema_details_unencrypted_token():
    unencrypted_secret = "LOOKS-LIKE-A-UUID"
    cds = factories.CDSCinemaDetailsFactory()
    cds_id = cds.id
    db.session.query(models.CDSCinemaDetails).filter(models.CDSCinemaDetails.id == cds_id).update(
        {"_cinemaApiToken": unencrypted_secret}
    )

    db.session.expunge(cds)
    db_cds = db.session.query(models.CDSCinemaDetails).filter(models.CDSCinemaDetails.id == cds_id).one()
    assert db_cds.cinemaApiToken == unencrypted_secret


def test_CDS_cinema_details_update_token():
    unencrypted_secret = "LOOKS-LIKE-A-UUID"
    cds = factories.CDSCinemaDetailsFactory()
    cds_id = cds.id

    cds.cinemaApiToken = unencrypted_secret
    db.session.commit()

    db.session.expunge(cds)
    db_cds = db.session.query(models.CDSCinemaDetails).filter(models.CDSCinemaDetails.id == cds_id).one()
    assert db_cds.cinemaApiToken == unencrypted_secret
