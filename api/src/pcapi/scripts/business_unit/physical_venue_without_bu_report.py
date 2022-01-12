import csv
import logging
import re
import time
import unicodedata

from pcapi.connectors.api_entreprises import get_by_offerer
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES
from pcapi.core.categories.subcategories import OnlineOfflinePlatformChoices
from pcapi.core.categories.subcategories import ReimbursementRuleChoices
from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.models import Offer
from pcapi.models.bank_information import BankInformation
from pcapi.models.bank_information import BankInformationStatus
from pcapi.repository import repository


logger = logging.getLogger(__name__)
reimbursable_subcategory_ids = [
    subcategory.id
    for subcategory in ALL_SUBCATEGORIES
    if (
        subcategory.online_offline_platform
        in [OnlineOfflinePlatformChoices.ONLINE.value, OnlineOfflinePlatformChoices.ONLINE_OR_OFFLINE.value]
        and subcategory.reimbursement_rule != ReimbursementRuleChoices.NOT_REIMBURSED.value
    )
]


def create_business_unit(venue, bank_information, business_unit_name=None):
    print("create_business_unit::venue", venue)
    print(f'Will create BusinessUnit for venueId {venue.id}, (isVirtual: {"Oui" if venue.isVirtual else "Non"})')
    bank_information = BankInformation(
        bic=bank_information.bic,
        iban=bank_information.iban,
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


def normalize_string(entry):
    nfkd_form = unicodedata.normalize("NFKD", entry)
    normalized_string = nfkd_form.encode("ASCII", "ignore")
    normalized_string = str(normalized_string, "utf-8")
    normalized_string = normalized_string.strip().lower()
    normalized_string = re.sub("[^A-Za-z0-9() -]+", "", normalized_string)
    return re.sub(" +", " ", normalized_string)


def address_from_full_address(full_address, postal_code):
    try:
        postal_code_index = full_address.index(postal_code)
        address = full_address[:postal_code_index]
    except ValueError:
        address = full_address
    return address


def have_bank_information(source):
    return source.bankInformation and source.bankInformation.status == BankInformationStatus.ACCEPTED


def venue_should_have_business_unit(venue):
    reimbursable_offer_check = True
    if venue.isVirtual == True:
        nb_offers = Offer.query.filter(
            Offer.subcategoryId.in_(reimbursable_subcategory_ids),
            Offer.venueId == venue.id,
            Offer.isActive == True,
        ).count()
        reimbursable_offer_check = nb_offers > 0
    return venue.businessUnitId is None and (venue.isVirtual is False or reimbursable_offer_check)


def get_offerer_business_units(offerer):
    """
    Look for business unit that use same bic and iban that the given offerer
    """
    offerer_iban = offerer.bankInformation.iban
    offerer_bic = offerer.bankInformation.bic
    return [
        venue.businessUnit
        for venue in offerer.managedVenues
        if (
            venue.businessUnit is not None
            and venue.businessUnit.bankAccount.iban == offerer_iban
            and venue.businessUnit.bankAccount.bic == offerer_bic
        )
    ]


def load_main_venue_siren_api_data(offerer):
    time.sleep(0.3)  # SIREN api is limited to 7 calls per seconds
    siren_api_data_for_offerer = get_by_offerer(offerer)
    siren_api_main_venue_data = siren_api_data_for_offerer["unite_legale"]["etablissement_siege"]
    if siren_api_main_venue_data:
        return {
            "name": siren_api_main_venue_data["enseigne_1"],
            "address": siren_api_main_venue_data["geo_adresse"],
            "address_geo_l4": siren_api_main_venue_data["geo_l4"],
            "address_geo_l5": siren_api_main_venue_data["geo_l5"],
            "postalCode": siren_api_main_venue_data["code_postal"],
            "city": siren_api_main_venue_data["libelle_commune"],
            "latitude": siren_api_main_venue_data["latitude"],
            "longitude": siren_api_main_venue_data["longitude"],
            "siret": siren_api_main_venue_data["siret"],
        }
    return None


def get_report_headers():
    return [
        "status",
        "offerer_id",
        "main_venue_id",
        "main_venue_siret",
        "api_siret",
        "main_venue_address",
        "api_normalized_address",
        "venue_data_created",
        "nb_venue_without_bu",
        "nb_siret_venue_without_bu",
        "with_reimbursable_offer_virtual_venue_id",
        "existing_offerer_iban_business_unit_ids",
        "business_unit_id",
        "business_unit_siret",
    ]


def write_report_row(writer, status, offerer, extra_data, main_venue=None, business_unit=None):
    data = [
        status,  # 0 status
        offerer.id,  # offerer_id
        main_venue.id if main_venue else "",  # main_venue_id
        main_venue.siret if main_venue else "",  # main_venue_siret
        extra_data["api_siret"],  # api_siret
        main_venue.dateCreated if main_venue else "",  # main_venue_date_created
        main_venue.address if main_venue else "",  # main_venue_address
        extra_data["api_normalized_address"],  # api_normalized_address
        extra_data["nb_venue_without_bu"],  # nb_venue_without_bu
        extra_data["nb_siret_venue_without_bu"],  # nb_siret_venue_without_bu
        extra_data["with_reimbursable_offer_virtual_venue_id"],  # with_reimbursable_offer_virtual_venue_id
        extra_data["existing_offerer_iban_business_unit_ids"],  # existing_offerer_iban_business_unit_id
        business_unit.id if business_unit else "",  # business_unit_id
        business_unit.siret if business_unit else "",  # business_unit_siret
    ]
    writer.writerow(data)


def run(report_file_name="report_business_unit_siren_api.csv", dry_run=True):
    offerers = Offerer.query.filter(Offerer.isActive == True).all()
    with open(f"/tmp/{report_file_name}", "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(get_report_headers())
        for offerer in offerers:
            if not have_bank_information(offerer):
                continue
            venues = [venue for venue in offerer.managedVenues if venue_should_have_business_unit(venue)]
            if len(venues) == 0:
                continue
            virtual_venues = [venue for venue in venues if venue.isVirtual == True]
            main_venue = None
            report_success_status = None
            report_extra_data = {
                "api_normalized_address": "",
                "api_siret": "",
                "nb_venue_without_bu": len(venues),
                "nb_siret_venue_without_bu": "",
                "with_reimbursable_offer_virtual_venue_id": virtual_venues[0].id if len(virtual_venues) > 0 else "",
                "existing_offerer_iban_business_unit_ids": "",
            }
            physical_venues = [venue for venue in venues if venue.isVirtual is False]
            if len(physical_venues) == 0:
                print("[no physical venues]")
                print(f"Offerer (id: {offerer.id}) have no physical venues.")
                print("Unable to handle it's virtual venue with reimbursable active offers.")
                write_report_row(writer, "SKIP_NO_PHYSICAL_VENUES", offerer, report_extra_data)
                continue
            existing_offerer_business_units = get_offerer_business_units(offerer)
            if len(existing_offerer_business_units) > 0:
                print("[existing offerer business unit]")
                print(
                    f"Offerer (id: {offerer.id}) already have {len(existing_offerer_business_units)} business unit with same bic and iban."
                )
                print(f"Unable to handle it's {len(venues)} venue without business unit.")
                report_extra_data["existing_offerer_iban_business_unit_ids"] = ", ".join(
                    [str(bu.id) for bu in existing_offerer_business_units]
                )
                write_report_row(
                    writer,
                    "SKIP_EXISTING_OFFERER_IBAN_BU",
                    offerer,
                    report_extra_data,
                )
                continue
            physical_venue_with_siret = [venue for venue in physical_venues if venue.siret is not None]
            nb_physical_venue_with_siret = len(physical_venue_with_siret)
            report_extra_data["nb_siret_venue_without_bu"] = nb_physical_venue_with_siret
            if nb_physical_venue_with_siret == 1:
                print("[single siret found]")
                main_venue = physical_venue_with_siret[0]
                existing_business_unit = BusinessUnit.query.filter(BusinessUnit.siret == main_venue.siret).one_or_none()
                if existing_business_unit is not None:
                    print("[business unit for main siret exist]")
                    write_report_row(
                        writer,
                        "SKIP_BU_WITH_VENUE_SIRET_ALREADY_EXIST",
                        offerer,
                        report_extra_data,
                        main_venue,
                        existing_business_unit,
                    )
                    continue
                report_success_status = "SUCCESS_SINGLE_SIRET_FOUND"
            elif nb_physical_venue_with_siret > 1:
                print("[multiple siret found]")
                print(f"Offerer (id: {offerer.id}) have {nb_physical_venue_with_siret} venues with a siret.")
                print(f"Unable to choose in order to handle it's {len(venues)} venue without business unit.")
                write_report_row(writer, "SKIP_MULTIPLE SIRET WITHOUT BU", offerer, report_extra_data)
                continue
            siren_api_data = None
            if main_venue == None:
                siren_api_data = load_main_venue_siren_api_data(offerer)
                if siren_api_data is None:
                    print("[no data from siren api]")
                    print(f"Offerer {offerer.id} have no existing data on siren api.")
                    print(f"Unable to choose in order to handle it's {len(venues)} venue without business unit.")
                    write_report_row(writer, "SKIP_NO_DATA_FROM_SIREN_API", offerer, report_extra_data)
                    continue
                existing_main_venue = [
                    venue for venue in offerer.managedVenues if venue.siret == siren_api_data["siret"]
                ]
                if len(existing_main_venue) > 0:
                    print("[main venue already exist]")
                    print(
                        f"Offerer {offerer.id} already have a venue (id: {existing_main_venue[0].id}) with the main venue siret: {siren_api_data['siret']}."
                    )
                    write_report_row(
                        writer, "SKIP_MAIN_VENUE_ALREADY_EXIST", offerer, report_extra_data, existing_main_venue[0]
                    )
                    continue
                report_extra_data["api_siret"] = siren_api_data["siret"]
                if siren_api_data["address"]:
                    api_address = address_from_full_address(siren_api_data["address"], siren_api_data["postalCode"])
                    normalized_api_address = normalize_string(api_address)
                    report_extra_data["api_normalized_address"] = normalized_api_address
                    possible_main_venues = [
                        venue for venue in physical_venues if normalized_api_address == normalize_string(venue.address)
                    ]
                    nb_possible_venues = len(possible_main_venues)
                    if nb_possible_venues == 1:
                        main_venue = possible_main_venues[0]
                        print("[match main venue from address]")
                        report_success_status = "SUCCESS_MATCH_API_ADDRESS"
                if main_venue == None:
                    venues_by_created_date = sorted(physical_venues, key=lambda venue: venue.dateCreated)
                    main_venue = venues_by_created_date[0]
                    print("[choose main venue by dateCreated]")
                    report_success_status = "SUCCESS_BY_DATE_CREATED"
            if main_venue != None:
                business_unit = None
                if not dry_run:
                    if siren_api_data:
                        print(f"assign siret {siren_api_data['siret']} to venue {main_venue.id}")
                        logger.info(
                            "Assign venue siret from entreprise.data.gouv.fr",
                            extra={
                                "venue": main_venue.id,
                                "venue_siret": main_venue.siret,
                                "api_siret": siren_api_data["siret"],
                            },
                        )
                        main_venue.siret = siren_api_data["siret"]
                        repository.save(main_venue)
                    print(
                        f"create business unit for offerer (id: {offerer.id}) with siret {main_venue.siret} for {len(venues)} venues without business unit"
                    )
                    business_unit = create_business_unit(main_venue, offerer.bankInformation)
                    for venue in venues:
                        if venue.postalCode == "4083":
                            # this postal code is in luxembourg, we have nothing to do
                            continue
                        logger.info(
                            "Assign businessUnitId to venue",
                            extra={
                                "venue": venue.id,
                                "business_unit": business_unit.id,
                            },
                        )
                        venue.businessUnitId = business_unit.id
                        repository.save(venue)
                write_report_row(writer, report_success_status, offerer, report_extra_data, main_venue, business_unit)
