from pcapi.core.geography.factories import AddressFactory
from pcapi.core.geography.models import Address
from pcapi.core.offerers.factories import OfferLocationFactory
from pcapi.core.offers.factories import OfferFactory
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
    good_location = OfferLocationFactory(
        address=good_address, offerer=location.offerer, venue=location.venue, label=location.label
    )
    offer = OfferFactory(offererAddress=location, venue=location.venue)
    assert location.addressId == address.id
    from pcapi.scripts.address.main import main

    main(apply=False)
    main(apply=True)
    main(apply=True)

    assert db.session.query(Address).filter(Address.city == "Perceval").count() == 1
    assert offer.offererAddressId == good_location.id
    assert not db.session.query(Address).filter(Address.id == address.id).one_or_none()


def test_with_multiple_duplicate_offer_location(db_session):
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
    location2 = OfferLocationFactory(address=address, label="rigolo")
    good_location = OfferLocationFactory(
        address=good_address, offerer=location.offerer, venue=location.venue, label=location.label
    )
    good_location2 = OfferLocationFactory(
        address=good_address, offerer=location2.offerer, venue=location2.venue, label=location2.label
    )
    offer = OfferFactory(offererAddress=location, venue=location.venue)
    offer2 = OfferFactory(offererAddress=location2, venue=location2.venue)
    assert location.addressId == address.id
    assert location2.addressId == address.id
    from pcapi.scripts.address.main import main

    main(apply=False)
    main(apply=True)
    main(apply=True)

    assert db.session.query(Address).filter(Address.city == "Perceval").count() == 1
    assert offer.offererAddressId == good_location.id
    assert offer2.offererAddressId == good_location2.id
    assert not db.session.query(Address).filter(Address.id == address.id).one_or_none()
