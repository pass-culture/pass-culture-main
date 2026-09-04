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


def test_fix_missing_inseeCode_with_existing_correct_address(db_session):
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

    assert db.session.query(Address).filter(Address.city == "Perceval").count() == 1
    assert location.addressId == good_address.id
