from pcapi.core.geography.factories import AddressFactory
from pcapi.core.geography.models import Address
from pcapi.core.offerers.factories import OfferLocationFactory
from pcapi.models import db


def test_fix_missing_inseeCode(db_session):
    address = AddressFactory(city="Perceval", inseeCode=None, banId="12345678901234")
    assert address.inseeCode is None
    from pcapi.scripts.address.main import main

    main(apply=False)
    main(apply=True)

    assert address.inseeCode == "12345"


def test_with_existing_correct_address(db_session):
    """if address has correct duplicate, change related locations to correct duplicate and delete the address"""
    address = AddressFactory(city="Perceval", inseeCode=None, banId="12345678901234")
    good_address = AddressFactory(
        city="Perceval",
        inseeCode="12345",
        banId="12345678901234",
        street=address.street,
        postalCode=address.postalCode,
        departmentCode=address.departmentCode,
        latitude=address.latitude,
        longitude=address.longitude,
        timezone=address.timezone,
    )
    location = OfferLocationFactory(address=address)
    assert location.addressId == address.id
    from pcapi.scripts.address.main import main

    main(apply=False)
    main(apply=True)

    assert db.session.query(Address).filter(Address.city == "Perceval").one() == good_address
    assert location.addressId == good_address.id


def test_with_duplicate_offer_location(db_session):
    """if address has correct duplicate and both have similar offerlocations, display log and don't do anything until PC-40918 is run"""
    address = AddressFactory(city="Perceval", inseeCode=None, banId="12345678901234")
    good_address = AddressFactory(
        city="Perceval",
        inseeCode="12345",
        banId="12345678901234",
        street=address.street,
        postalCode=address.postalCode,
        departmentCode=address.departmentCode,
        latitude=address.latitude,
        longitude=address.longitude,
        timezone=address.timezone,
    )
    location = OfferLocationFactory(address=address)
    OfferLocationFactory(address=good_address, offerer=location.offerer, venue=location.venue, label=location.label)
    assert location.addressId == address.id
    from pcapi.scripts.address.main import main

    main(apply=False)
    main(apply=True)

    assert db.session.query(Address).filter(Address.city == "Perceval").count() == 2
    assert location.addressId == address.id
