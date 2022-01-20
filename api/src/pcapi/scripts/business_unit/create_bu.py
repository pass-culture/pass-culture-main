import logging

from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.models import Offerer
from pcapi.models.bank_information import BankInformation
from pcapi.models.bank_information import BankInformationStatus
from pcapi.repository import repository


logger = logging.getLogger(__name__)


"""
To test it on staging before merge :
$ kubectl get pods -n staging
NAME                                                      READY   STATUS      RESTARTS   AGE
[...]
staging-pcapi-console-546c6bc847-hgnp9                    1/1     Running     0          2d1h
[...]
$ kubectl cp ./src/pcapi/scripts/business_unit/create_bu.py staging/staging-pcapi-console-546c6bc847-hgnp9:/tmp/create_bu.py
$ kubectl cp ./src/pcapi/scripts/business_unit/reset_venues_invalid_sirets.py staging/staging-pcapi-console-546c6bc847-hgnp9:/tmp/reset_venues_invalid_sirets.py
$ pc -e staging bash
root@staging-pcapi-console-546c6bc847-hgnp9:/usr/src/app# mv /tmp/reset_venues_invalid_sirets.py src/pcapi/scripts/
root@staging-pcapi-console-546c6bc847-hgnp9:/usr/src/app# mv /tmp/create_bu.py src/pcapi/scripts/

$ pc -e staging python
staging >>> from pcapi.scripts.reset_venues_invalid_sirets import reset_venues_invalid_sirets
staging >>> reset_venues_invalid_sirets(dry_run=False) # or True, you choose

staging >>> # if nullable applicationId migration is not yet done
staging >>> from pcapi.models import db
staging >>> from pcapi.validation.models import bank_information as bi_val
staging >>> from sqlalchemy import Column
staging >>> from sqlalchemy import Integer
staging >>> from pcapi.models import bank_information
staging >>> from sqlalchemy.schema import Table
staging >>>
staging >>>
staging >>> Table("bank_information", bank_information.BankInformation.metadata,
        ...     Column('applicationId', Integer, nullable=True, index=True, unique=True),
        ...     extend_existing=True,
        ...     autoload_with=db.engine
        ... )
staging >>> # bypass BankInformation validation cause staging IBAN are not valid!
staging >>> def fake_val(bank_information, api_errors):
staging >>>     return api_errors
staging >>>
staging >>>
staging >>> bi_val.validate = fake_val


staging >>> from pcapi.scripts.create_bu import create_all_business_units
staging >>> create_all_business_units()
staging >>> from pcapi.scripts.purge_virtual_venue_business_units import purge_virtual_venue_business_units
staging >>> # Clear some business unit with virtual venues
staging >>> purge_virtual_venue_business_units()
"""


def have_bank_information(source):
    return source.bankInformation and source.bankInformation.status == BankInformationStatus.ACCEPTED


def create_business_unit(venue, bank_information, business_unit_name=None):
    print(f'Will create BusinessUnit for venueId {venue.id}, (isVirtual: {"Oui" if venue.isVirtual else "Non"})')

    bank_information = BankInformation(
        bic=bank_information.bic,
        iban=bank_information.iban,
        applicationId=bank_information.applicationId,
        status=BankInformationStatus.ACCEPTED,
    )
    business_unit = BusinessUnit(
        name=business_unit_name or venue.publicName or venue.name,
        siret=venue.siret,
        bankAccount=bank_information,
    )
    venue.businessUnit = business_unit

    repository.save(bank_information, business_unit, venue)
    logger.info("Create BusinessUnit", extra={"venue": venue.id, "siret": venue.siret})
    return business_unit


def create_business_units_for_venues_with_siret(venues, offerer_bank_information=None):
    business_units = []
    for venue in venues:
        if venue.businessUnitId:
            continue
        if venue.siret:
            if have_bank_information(venue):
                business_units.append(create_business_unit(venue, venue.bankInformation))
            elif offerer_bank_information:
                business_units.append(create_business_unit(venue, offerer_bank_information))
    return business_units


def create_offerer_business_units(venues, bank_information):
    business_units = []
    for venue in venues:
        if venue.businessUnitId:
            continue
        if venue.siret and (
            not have_bank_information(venue)
            or (
                venue.bankInformation.bic == bank_information.bic
                and venue.bankInformation.iban == bank_information.iban
            )
        ):
            business_units.append(create_business_unit(venue, bank_information))
    return business_units


def populate_business_unit(business_unit, venues):
    for venue in venues:
        print("Processing venue %i" % venue.id)
        if venue.businessUnitId:
            continue
        if not venue.siret and (
            not have_bank_information(venue)
            or (
                venue.bankInformation.bic == business_unit.bankAccount.bic
                and venue.bankInformation.iban == business_unit.bankAccount.iban
            )
        ):
            venue.businessUnitId = business_unit.id
            repository.save(venue)


def create_offerer_business_units_witout_siret(venues, bank_information):
    business_unit = None
    for venue in venues:
        if venue.businessUnitId:
            continue
        if not venue.siret and (
            not have_bank_information(venue)
            or (
                venue.bankInformation.bic == bank_information.bic
                and venue.bankInformation.iban == bank_information.iban
            )
        ):
            if not business_unit:
                business_unit = create_business_unit(venue, bank_information)
            else:
                venue.businessUnitId = business_unit.id
                repository.save(venue)
    return [business_unit]


def get_tmp_business_unit_id(bank_information):
    return f"{bank_information.bic}:{bank_information.iban}"


def create_business_units_without_siret(venues):
    business_units = {}
    nb_business_units_without_siret = 0
    for venue in venues:
        if venue.businessUnitId:
            continue
        if not venue.siret and have_bank_information(venue):
            tmp_id = get_tmp_business_unit_id(venue.bankInformation)
            if tmp_id in business_units:
                venue.businessUnitId = business_units[tmp_id].id
                repository.save(venue)
            else:
                nb_business_units_without_siret += 1
                business_units[tmp_id] = create_business_unit(
                    venue, venue.bankInformation, f"Point de remboursement #{nb_business_units_without_siret}"
                )
    return business_units.values()


def create_all_business_units():
    offerers = Offerer.query.all()
    created_business_units = []
    for offerer in offerers:
        offerer_bank_information = None
        venues = offerer.managedVenues
        if have_bank_information(offerer):
            # venues that have a siret and no proper bank information
            # create a business unit with offerer bank_information bic and iban
            business_units = create_offerer_business_units(venues, offerer.bankInformation)
            created_business_units = [*created_business_units, *business_units]
            if len(business_units) == 1:
                # we have a single "offerer business unit"
                # append to it venues that have no siret and:
                # * bank_informatin with similar bic/iban than offerer bank_information
                # * or no bank_informations
                populate_business_unit(business_units[0], venues)
            else:
                # create a business unit without siret
                # for venue that have no siret and:
                # * bank_informatin with similar bic/iban than offerer bank_information
                # * or no bank_informations
                created = create_offerer_business_units_witout_siret(venues, offerer.bankInformation)
                created_business_units = [*created_business_units, *created]

        # create one business unit for each venue with siret and bank_information
        created = create_business_units_for_venues_with_siret(venues, offerer_bank_information)
        created_business_units = [*created_business_units, *created]

        # populate venue with siret BusinessUnit with lonely venue without siret using same bank_informations
        for business_unit in created:
            populate_business_unit(business_unit, venues)

        # finaly create business_unit for venue without siret that have bank_information
        created = create_business_units_without_siret(venues)
        created_business_units = [*created_business_units, *created]
    return created_business_units
