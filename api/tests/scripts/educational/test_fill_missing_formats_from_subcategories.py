import os

import pytest

from pcapi.core.categories.subcategories_v2 import EVENEMENT_CINE
from pcapi.core.categories.subcategories_v2 import EacFormat
from pcapi.core.categories.subcategories_v2 import SEANCE_CINE
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.models import db
from pcapi.scripts.educational.fill_missing_formats_from_subcategories import run


pytestmark = pytest.mark.usefixtures("db_session")


def test_run_one_offer(tmp_path) -> None:
    out_path = tmp_path / "offer.ids"
    offer = CollectiveOfferFactory(formats=None, subcategoryId=SEANCE_CINE.id)

    ids = run(out_path=out_path)
    assert ids == {offer.id}

    db.session.refresh(offer)
    assert offer.formats == SEANCE_CINE.formats
    assert out_path.read_text() == f"{offer.id}"


def test_run_update_many_ignore_many(tmp_path) -> None:
    out_path = tmp_path / "offer.ids"

    offer1 = CollectiveOfferFactory(formats=None, subcategoryId=SEANCE_CINE.id)
    offer2 = CollectiveOfferFactory(formats=None, subcategoryId=EVENEMENT_CINE.id)

    ignored = CollectiveOfferFactory.create_batch(2, formats=[EacFormat.CONCERT])

    ids = run(out_path=out_path)
    assert ids == {offer1.id, offer2.id}

    db.session.refresh(offer1)
    db.session.refresh(offer2)
    assert offer1.formats == SEANCE_CINE.formats
    assert offer1.formats == EVENEMENT_CINE.formats

    content = out_path.read_text()
    assert not any(str(offer.id) in content for offer in ignored)


def test_run_no_offer_to_update(tmp_path) -> None:
    out_path = tmp_path / "offer.ids"
    offer = CollectiveOfferFactory(formats=SEANCE_CINE.formats, subcategoryId=SEANCE_CINE.id)

    ids = run(out_path=out_path)
    assert ids == set()

    db.session.refresh(offer)
    assert offer.formats == SEANCE_CINE.formats
    assert out_path.read_text() == ""


def test_run_no_offer_at_all(tmp_path) -> None:
    out_path = tmp_path / "offer.ids"

    ids = run(out_path=out_path)
    assert ids == set()
    assert out_path.read_text() == ""


def test_run_dry_run_enabled(tmp_path) -> None:
    out_path = tmp_path / "offer.ids"
    offer = CollectiveOfferFactory(formats=None, subcategoryId=SEANCE_CINE.id)

    ids = run(dry_run=True, out_path=out_path)
    assert ids == {offer.id}

    db.session.refresh(offer)
    assert offer.formats is None
    assert out_path.read_text() == f"{offer.id}"


def test_run_no_output_path(tmp_path) -> None:
    out_path = tmp_path / "offer.ids"
    offer = CollectiveOfferFactory(formats=None, subcategoryId=SEANCE_CINE.id)

    ids = run(out_path=None)
    assert ids == {offer.id}

    db.session.refresh(offer)
    assert offer.formats == SEANCE_CINE.formats
    assert not os.path.exists(out_path)
