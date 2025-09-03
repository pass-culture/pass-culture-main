import pytest

from pcapi.core.offers import factories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferMetaData
from pcapi.models import db
from pcapi.scripts.clean_empty_offer_metadata.main import delete_empty_offer_metadata


@pytest.mark.usefixtures("db_session")
def test_delete_empty_offer_metadata(db_session):
    offer_1 = factories.OfferFactory()
    offer_2 = factories.OfferFactory()

    empty_meta = factories.OfferMetaDataFactory(
        offer=offer_1,
        videoUrl=None,
        videoDuration=None,
        videoExternalId=None,
        videoThumbnailUrl=None,
        videoTitle=None,
    )

    non_empty_meta = factories.OfferMetaDataFactory(
        offer=offer_2,
        videoUrl="https://www.youtube.com/watch?v=ZjSlDZhwHs8",
        videoDuration=3,
        videoExternalId="ZjSlDZhwHs8",
        videoThumbnailUrl=None,
        videoTitle="Gilbert Organisé",
    )

    db.session.add_all([empty_meta, non_empty_meta])
    db.session.commit()

    delete_empty_offer_metadata()

    assert db_session.query(Offer).count() == 2
    assert db_session.query(OfferMetaData).count() == 1
    assert db_session.query(OfferMetaData).first().videoUrl == "https://www.youtube.com/watch?v=ZjSlDZhwHs8"
