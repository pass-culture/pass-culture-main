from collections import defaultdict
import csv
import logging
import os
from typing import Optional

from pcapi.connectors.api_entreprises import get_by_offerer
from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.models.bank_information import BankInformationStatus
from pcapi.repository import repository


logger = logging.getLogger(__name__)


class MissingBusinessUnitInformationsException(Exception):
    pass


def have_bank_information(source):
    return source.bankInformation and source.bankInformation.status == BankInformationStatus.ACCEPTED


def load_main_venue_siren_api_data(offerer):
    siren_api_data_for_offerer = get_by_offerer(offerer)
    siren_api_main_venue_data = siren_api_data_for_offerer["unite_legale"]["etablissement_siege"]

    return {
        "name": siren_api_main_venue_data["enseigne_1"],
        "address": siren_api_main_venue_data["geo_l4"],
        "postalCode": siren_api_main_venue_data["code_postal"],
        "city": siren_api_main_venue_data["libelle_commune"],
        "latitude": siren_api_main_venue_data["latitude"],
        "longitude": siren_api_main_venue_data["longitude"],
        "siret": siren_api_main_venue_data["siret"],
    }


def create_venue_from_siren_api_data(offerer_id, siren_api_data):
    return Venue(
        managingOffererId=offerer_id,
        name=siren_api_data["name"],
        publicName=siren_api_data["name"],
        address=siren_api_data["address"],
        postalCode=siren_api_data["postalCode"],
        city=siren_api_data["city"],
        latitude=siren_api_data["latitude"],
        longitude=siren_api_data["longitude"],
        siret=siren_api_data["siret"],
        audioDisabilityCompliant=False,
        mentalDisabilityCompliant=False,
        motorDisabilityCompliant=False,
        visualDisabilityCompliant=False,
        isPermanent=True,
    )


class PreBusinessUnitStatus:
    DRAFT = "DRAFT"
    CREATED = "CREATED"

    DRAFT_NO_MAIN_SIRET = "DRAFT_NO_MAIN_SIRET"
    DRAFT_API_SIRET_NOT_MATCH = "DRAFT_API_SIRET_NOT_MATCH"
    DRAFT_API_SIRET_MATCH_MANAGED_VENUES = "DRAFT_API_SIRET_MATCH_MANAGED_VENUES"
    DRAFT_API_SIRET_NOT_MATCH_MANAGED_VENUE = "DRAFT_API_SIRET_NOT_MATCH_MANAGED_VENUE"
    DRAFT_API_ADDRESS_NOT_MATCH = "DRAFT_API_ADDRESS_NOT_MATCH"

    PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE = "PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE"
    PENDING_API_ADDRESS_MATCH = "PENDING_API_ADDRESS_MATCH"
    PENDING_API_ADDRESS_MATCH_MANAGED_VENUE = "PENDING_API_ADDRESS_MATCH_MANAGED_VENUE"

    READY = "READY"
    READY_API_SIRET_MATCH = "READY_API_SIRET_MATCH"
    READY_API_SIRET_MATCH_MANAGED_VENUE = "READY_API_SIRET_MATCH_MANAGED_VENUE"
    READY_API_ADDRESS_MATCH = "READY_API_ADDRESS_MATCH"
    READY_API_ADDRESS_MATCH_MANAGED_VENUE = "READY_API_ADDRESS_MATCH_MANAGED_VENUE"
    READY_MAIN_VENUE_CREATED = "READY_MAIN_VENUE_CREATED"

    END_API_ADDRESS_MATCH_VENUE_NOT_ASSIGNABLE = "END_API_ADDRESS_MATCH_VENUE_NOT_ASSIGNABLE"
    END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE = "END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE"
    END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE = "END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE"


PRE_BUSINESS_UNIT_DRAFT_STATUS = [
    PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET,
    PreBusinessUnitStatus.DRAFT_API_SIRET_NOT_MATCH,
    PreBusinessUnitStatus.DRAFT_API_SIRET_MATCH_MANAGED_VENUES,
    PreBusinessUnitStatus.DRAFT_API_SIRET_NOT_MATCH_MANAGED_VENUE,
    PreBusinessUnitStatus.DRAFT_API_ADDRESS_NOT_MATCH,
]

PRE_BUSINESS_UNIT_PENDING_STATUS = [
    PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE,
    PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH,
    PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE,
]

PRE_BUSINESS_UNIT_READY_STATUS = [
    PreBusinessUnitStatus.READY,
    PreBusinessUnitStatus.READY_API_SIRET_MATCH,
    PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE,
    PreBusinessUnitStatus.READY_API_ADDRESS_MATCH,
    PreBusinessUnitStatus.READY_API_ADDRESS_MATCH_MANAGED_VENUE,
    PreBusinessUnitStatus.READY_MAIN_VENUE_CREATED,
]

PRE_BUSINESS_UNIT_END_STATUS = [
    PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
    PreBusinessUnitStatus.END_API_ADDRESS_MATCH_VENUE_NOT_ASSIGNABLE,
    PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
]

PRE_BUSINESS_UNIT_REPORT_STATUS = [
    *PRE_BUSINESS_UNIT_DRAFT_STATUS,
    *PRE_BUSINESS_UNIT_PENDING_STATUS,
    *PRE_BUSINESS_UNIT_READY_STATUS,
    *PRE_BUSINESS_UNIT_END_STATUS,
    PreBusinessUnitStatus.CREATED,
]


class PreBusinessUnit:
    bic: str
    ban: str
    name: str
    bank_information_id: Optional[str]
    business_unit: Optional[BusinessUnit]
    siret: Optional[str]
    venues: list[Venue]
    venues_bank_informations: dict
    status: str
    # main_venue = Optional[Venue]

    def __init__(self, bic, iban, bank_information_id=None):
        self.bic = bic
        self.iban = iban
        self.bank_information_id = bank_information_id

        self.name = ""
        self.business_unit = None
        self.siret = None
        self.main_venue_id = None
        self.venues = []
        self.venues_bank_informations = {}
        self.status = PreBusinessUnitStatus.DRAFT

    def __to_dict__(self):
        return self.__dict__

    @staticmethod
    def get_pre_business_unit_id(bic, iban):
        return f"{bic}:{iban}"

    @property
    def id(self):
        return self.get_pre_business_unit_id(self.bic, self.iban)

    @property
    def siret_list(self):
        return {venue.siret for venue in self.venues if venue.siret is not None}

    @property
    def venue_ids(self):
        return [venue.id for venue in self.venues]

    def add_venue(self, venue, venue_bank_information=None):
        self.venues.append(venue)
        if venue.bankInformation:
            self.venues_bank_informations[venue.id] = venue.bankInformation.id

    def get_main_venue(self):
        if not self.siret:
            return None
        for venue in self.venues:
            if venue.siret == self.siret:
                return venue
        return None

    def get_venue_id_from_siret(self, siret):
        for venue in self.venues:
            if venue.siret == siret:
                return venue.id
        return None

    def get_bank_information_id(self):
        if self.bank_information_id:
            return self.bank_information_id
        nb_bank_informations = len(set(self.venues_bank_informations.values()))
        if nb_bank_informations == 1:
            return list(self.venues_bank_informations.values())[0]
        if self.siret and nb_bank_informations > 1:
            main_venue = self.get_main_venue()
            if main_venue.id in self.venues_bank_informations:
                return self.venues_bank_informations[main_venue.id]
            return list(self.venues_bank_informations.values())[0]
        return None

    def fill_data_from_siret(self, siret):
        self.siret = siret
        self.bank_information_id = self.get_bank_information_id()
        self.name = self.get_name()

    def get_name(self):
        main_venue = self.get_main_venue()
        return main_venue.name

    def create_business_unit(self):
        if not self.siret or not self.bank_information_id:
            raise MissingBusinessUnitInformationsException(
                f"Not possible to create BusinessUnit with siret: {self.siret} and bank_information_id: {self.bank_information_id}"
            )

        business_unit = BusinessUnit(
            name=self.name,
            siret=self.siret,
            bankAccountId=self.bank_information_id,
        )
        repository.save(business_unit)
        for venue in self.venues:
            venue.businessUnitId = business_unit.id

        repository.save(*self.venues)
        self.status = PreBusinessUnitStatus.CREATED
        return business_unit

    def compute_initial_status(self):
        nb_sirets = len(self.siret_list)
        if self.business_unit is not None:
            self.status = PreBusinessUnitStatus.CREATED
        elif nb_sirets == 1:
            self.fill_data_from_siret(list(self.siret_list)[0])
            self.status = PreBusinessUnitStatus.READY
        else:
            self.status = PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET


class OffererBusinessUnitBuilder:
    offerer: Offerer
    venues: list[Venue]
    pre_business_units: list[PreBusinessUnit]
    siren_api_data: Optional[dict]

    def __init__(self, offerer):

        self.siren_api_data = None

        self.offerer = offerer
        self.venues = offerer.managedVenues

    def get_offerer_siret_list(self):
        return [venue.siret for venue in self.offerer.managedVenues if venue.siret]

    def get_for_statuses(self, statuses):
        return [pre_bu for pre_bu in self.pre_business_units.values() if pre_bu.status in statuses]

    def get_siret_status(self, siret):
        for pre_bu in self.pre_business_units.values():
            if siret in pre_bu.siret_list:
                return pre_bu.status
        return None

    def get_venue_id_status(self, siret):
        for pre_bu in self.pre_business_units.values():
            if siret in pre_bu.venue_ids:
                return pre_bu.status
        return None

    def report_by_status(self):
        report = defaultdict(lambda: 0)
        for pre_bu in self.pre_business_units.values():
            report[pre_bu.status] += 1
        return report

    def build_pre_business_units(self):
        pre_business_units = {}

        offerer_pre_bu = None
        if have_bank_information(self.offerer):
            offerer_pre_bu = PreBusinessUnit(
                self.offerer.bankInformation.bic, self.offerer.bankInformation.iban, self.offerer.bankInformation.id
            )
            pre_business_units[offerer_pre_bu.id] = offerer_pre_bu

        for venue in self.venues:
            pre_bu = None
            if have_bank_information(venue):
                pre_bu_id = PreBusinessUnit.get_pre_business_unit_id(
                    venue.bankInformation.bic, venue.bankInformation.iban
                )
                if pre_bu_id in pre_business_units:
                    pre_bu = pre_business_units.get(pre_bu_id)
                else:
                    pre_bu = PreBusinessUnit(venue.bankInformation.bic, venue.bankInformation.iban)
                pre_bu.add_venue(venue, venue.bankInformation)
            elif offerer_pre_bu:
                offerer_pre_bu.add_venue(venue)

            if pre_bu:
                pre_business_units[pre_bu.id] = pre_bu

        for pre_bu in pre_business_units.values():
            pre_bu.compute_initial_status()

        self.pre_business_units = pre_business_units
        return self.pre_business_units

    def get_main_venue_siren_api_data(self):
        if not self.siren_api_data:
            self.siren_api_data = load_main_venue_siren_api_data(self.offerer)
        return self.siren_api_data

    def process_ready(self, status_to_process):
        """
        All ready statuses have all needed informations to create BusinessUnit from PreBusinessUnit.
        Let's do it.
        """

        business_unit_list = self.get_for_statuses(status_to_process)
        for pre_bu in business_unit_list:
            pre_bu.create_business_unit()

    def process_draft_no_main_siret(self):
        """
        We didn't found a unique SIRET for theses PreBusinessUnit
        Here we'll try to match "api siren" main SIRET with one of the PreBusinessUnit SIRET
        """

        siren_api_data = self.get_main_venue_siren_api_data()
        main_siret = siren_api_data["siret"]

        business_unit_list = self.get_for_statuses([PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET])
        for pre_bu in business_unit_list:
            if main_siret in list(pre_bu.siret_list):
                pre_bu.siret = main_siret
                pre_bu.fill_data_from_siret(main_siret)
                pre_bu.status = PreBusinessUnitStatus.READY_API_SIRET_MATCH
            else:
                pre_bu.status = PreBusinessUnitStatus.DRAFT_API_SIRET_NOT_MATCH

    def process_draft_api_siret_not_match(self):
        """
        "api siren" main SIRET is not part of PreBusinessUnit SIRET
        Here we try to match it with a siret in offerer's managed venues
        """
        siren_api_data = self.get_main_venue_siren_api_data()
        main_siret = siren_api_data["siret"]

        business_unit_list = self.get_for_statuses([PreBusinessUnitStatus.DRAFT_API_SIRET_NOT_MATCH])
        for pre_bu in business_unit_list:
            if main_siret in self.get_offerer_siret_list():
                pre_bu.status = PreBusinessUnitStatus.DRAFT_API_SIRET_MATCH_MANAGED_VENUES
            else:
                pre_bu.status = PreBusinessUnitStatus.DRAFT_API_SIRET_NOT_MATCH_MANAGED_VENUE

    def process_draft_api_siret_match_managed_venues(self):
        """
        We found the offerer main SIRET in offerer's mannaged venues
        Here we check that it's not already part of a BusinessUnit or PreBusinessUnit
        """
        siren_api_data = self.get_main_venue_siren_api_data()
        main_siret = siren_api_data["siret"]

        business_unit_list = self.get_for_statuses([PreBusinessUnitStatus.DRAFT_API_SIRET_MATCH_MANAGED_VENUES])
        for pre_bu in business_unit_list:
            main_venue_assignable = False
            siret_pre_bu_status = self.get_siret_status(main_siret)

            main_venue = None
            if not siret_pre_bu_status:
                main_venue = Venue.query.filter(
                    Venue.managingOffererId == self.offerer.id,
                    Venue.siret == main_siret,
                ).one_or_none()
                if main_venue and not main_venue.businessUnitId:
                    main_venue_assignable = True

            if main_venue_assignable:
                pre_bu.siret = main_siret
                pre_bu.venues.append(main_venue)
                pre_bu.fill_data_from_siret(main_siret)
                pre_bu.status = PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE
            else:
                pre_bu.status = PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE

    def process_draft_api_siret_not_match_managed_venue(self):
        """
        The main SIRET doesn't exist on offerer's managed venue
        Here we try to match main venue address within PreBusinessUnit venues
        """
        siren_api_data = self.get_main_venue_siren_api_data()
        main_siret = siren_api_data["siret"]
        main_address = siren_api_data["address"]
        main_postal_code = siren_api_data["postalCode"]
        main_city = siren_api_data["city"]

        business_unit_list = self.get_for_statuses([PreBusinessUnitStatus.DRAFT_API_SIRET_NOT_MATCH_MANAGED_VENUE])
        for pre_bu in business_unit_list:
            venue_match_address = []
            for venue in pre_bu.venues:
                if venue.siret:
                    continue

                if all(
                    check
                    for check in [
                        main_address == venue.address,
                        main_postal_code == venue.postalCode,
                        main_city == venue.city,
                    ]
                ):
                    venue_match_address.append(venue)
            if len(venue_match_address) == 1:
                pre_bu.siret = main_siret
                main_venue = venue_match_address[0]
                pre_bu.main_venue_id = main_venue.id
                pre_bu.status = PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH
            else:
                pre_bu.status = PreBusinessUnitStatus.DRAFT_API_ADDRESS_NOT_MATCH

    def process_pending_api_address_match(self):
        """
        Main venue have been found in PreBusinessUnit venue by matching the address.
        Here we assign main the main SIRET to this venue
        """
        business_unit_list = self.get_for_statuses([PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH])
        for idx, pre_bu in enumerate(business_unit_list):
            # we cannot create offere main venue a second time
            if idx > 0:
                pre_bu.status = PreBusinessUnitStatus.END_API_ADDRESS_MATCH_VENUE_NOT_ASSIGNABLE
            else:
                main_venue = Venue.query.get(pre_bu.main_venue_id)
                if main_venue.siret:
                    logger.error("Unable to set SIRET on venue", extra={"venue": main_venue.id, "siret": pre_bu.siret})
                else:
                    main_venue.siret = pre_bu.siret
                    repository.save(main_venue)
                    logger.info("Set SIRET on venue", extra={"venue": main_venue.id, "siret": pre_bu.siret})
                    pre_bu.fill_data_from_siret(main_venue.siret)
                    pre_bu.status = PreBusinessUnitStatus.READY_API_ADDRESS_MATCH

    def process_draft_api_address_not_match(self):
        """
        The main SIRET doesn't exist on offerer's managed venue
        and the main address doesn't match any of the PreBusinessUnit venues
        Here we try to match the address within offerer's managed venues
        """
        siren_api_data = self.get_main_venue_siren_api_data()
        main_siret = siren_api_data["siret"]
        main_address = siren_api_data["address"]
        main_postal_code = siren_api_data["postalCode"]
        main_city = siren_api_data["city"]

        business_unit_list = self.get_for_statuses([PreBusinessUnitStatus.DRAFT_API_ADDRESS_NOT_MATCH])
        for pre_bu in business_unit_list:
            venue_match_address = []
            for venue in self.offerer.managedVenues:
                if all(
                    check
                    for check in [
                        main_address == venue.address,
                        main_postal_code == venue.postalCode,
                        main_city == venue.city,
                    ]
                ):
                    venue_match_address.append(venue)

            if len(venue_match_address) == 1:
                main_venue = venue_match_address[0]
                if main_venue.siret or main_venue.businessUnitId or self.get_venue_id_status(main_venue.id) is not None:
                    pre_bu.status = PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE
                else:
                    pre_bu.siret = main_siret
                    main_venue = venue_match_address[0]
                    pre_bu.main_venue_id = main_venue.id
                    pre_bu.venues.append(main_venue)
                    pre_bu.status = PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE
            elif len(venue_match_address) == 0:
                pre_bu.status = PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE
            else:
                pre_bu.status = PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE

    def process_pending_api_address_match_managed_venue(self):
        """
        Main venue have been found in offerer's managed venues by matching the address.
        Here we assign main the main SIRET to this venue and append it to the PreBusinessUnit
        """
        business_unit_list = self.get_for_statuses([PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE])
        for idx, pre_bu in enumerate(business_unit_list):
            # we cannot create offere main venue a second time
            if idx > 0:
                pre_bu.status = PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE
            else:
                main_venue = Venue.query.get(pre_bu.main_venue_id)

                if main_venue.siret:
                    logger.error("Unable to set SIRET on venue", extra={"venue": main_venue.id, "siret": pre_bu.siret})
                else:
                    main_venue.siret = pre_bu.siret
                    repository.save(main_venue)
                    logger.info("Set SIRET on venue", extra={"venue": main_venue.id, "siret": pre_bu.siret})
                    pre_bu.fill_data_from_siret(main_venue.siret)
                    pre_bu.status = PreBusinessUnitStatus.READY_API_ADDRESS_MATCH_MANAGED_VENUE

    def process_pending_api_address_not_match_managed_venue(self):
        """
        The main venue haven't been found with neither SIRET or address match
        Here we create a new venue from "siren api" data and append it to the PreBusinessUnit
        """
        business_unit_list = self.get_for_statuses([PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE])

        for idx, pre_bu in enumerate(business_unit_list):
            # we cannot create offere main venue a second time
            if idx > 0:
                pre_bu.status = PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE
            else:
                siren_api_data = self.get_main_venue_siren_api_data()
                main_venue = create_venue_from_siren_api_data(self.offerer.id, siren_api_data)
                repository.save(main_venue)
                logger.info(
                    "Create main venue from siren api data",
                    extra={"venue": main_venue.id, "siren_api_data": siren_api_data},
                )

                pre_bu.venues.append(main_venue)
                pre_bu.siret = main_venue.siret
                pre_bu.fill_data_from_siret(main_venue.siret)
                pre_bu.status = PreBusinessUnitStatus.READY_MAIN_VENUE_CREATED


class PreBusinessUnitReport:
    report: dict

    def __init__(self):
        self.report = {}
        for status in PRE_BUSINESS_UNIT_REPORT_STATUS:
            self.report[status] = {
                "offerer_ids": set(),
                "venue_ids": set(),
                "nb_pre_business_unit": 0,
                "pre_business_unit_ids": set(),
            }

    def add_offerer_pre_business_units(self, offerer_id, pre_business_unit_list):
        for pre_business_unit in pre_business_unit_list.values():
            if len(pre_business_unit.venue_ids):
                self.report[pre_business_unit.status]["venue_ids"].update(pre_business_unit.venue_ids)
                self.report[pre_business_unit.status]["offerer_ids"].add(offerer_id)
                self.report[pre_business_unit.status]["nb_pre_business_unit"] += 1
                self.report[pre_business_unit.status]["pre_business_unit_ids"].add(pre_business_unit.id)

    def print_bank_information_intersect_not_ready(self, data):
        print("###")
        not_ready_bic_iban = set()
        for st in self.report:
            if st in PRE_BUSINESS_UNIT_READY_STATUS:
                continue
            not_ready_bic_iban.update(self.report[st]["pre_business_unit_ids"])

        not_ready_bic_iban_in_data = list(set(data) & not_ready_bic_iban)

        print(not_ready_bic_iban_in_data)
        print(len(not_ready_bic_iban_in_data))
        print("###")

    def print_bank_information_intersect_ready(self, data):
        print("###")
        ready_bic_iban = set()
        for st in self.report:
            if st in PRE_BUSINESS_UNIT_READY_STATUS:
                continue
            ready_bic_iban.update(self.report[st]["pre_business_unit_ids"])

        ready_bic_iban_in_data = list(set(data) & ready_bic_iban)

        print(ready_bic_iban_in_data)
        print(len(ready_bic_iban_in_data))
        print("###")

    def export_offerer_ids_to_csv(self, file_path, status_to_export):
        if os.path.isfile(file_path):
            raise Exception(f"File already exist ! Cannot export offerer_ids in {file_path}.")

        with open(file_path, "w") as file:
            writer = csv.writer(file)
            for offerer_id in self.report[status_to_export]["offerer_ids"]:
                writer.writerow([offerer_id])
        file.close()


def process_statuses(builder, status_to_process):
    """
    Processing DRAFT statuses will have folowing output:
        Some PreBusinessUnit ready to create BusinessUnit:
            * READY,
            * READY_API_SIRET_MATCH,
            * READY_API_SIRET_MATCH_MANAGED_VENUE,
        Some PreBusinessUnit in a PENDING state:
            * PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE
            * PENDING_API_ADDRESS_MATCH
            * PENDING_API_ADDRESS_MATCH_MANAGED_VENUE
        Some PreBusinessUnit that cannot create BusinessUnit:
            * END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE
            * END_API_ADDRESS_MATCH_VENUE_NOT_ASSIGNABLE
            * END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE

    Processing PENDING statuses will have folowing output:
        Some PreBusinessUnit ready to create BusinessUnit:
        Here we will perform database updates (create venue, assign siret to venue)
            * PreBusinessUnitStatus.READY_API_ADDRESS_MATCH,
            * PreBusinessUnitStatus.READY_API_ADDRESS_MATCH_MANAGED_VENUE,
            * PreBusinessUnitStatus.READY_MAIN_VENUE_CREATED,
        Some PreBusinessUnit that cannot create BusinessUnit:
        When multiple PreBusinessUnit have match the main venue, only the first one can become READY
            * END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE

    Processing READY statuses will create BusinessUnit.
    The only output status here is CREATED
    """

    # We didn't found a unique SIRET for theses PreBusinessUnit
    # Here we'll try to match "api siren" main SIRET with one of the PreBusinessUnit SIRET
    if PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET in status_to_process:
        builder.process_draft_no_main_siret()

    # "api siren" main SIRET is not part of PreBusinessUnit SIRET
    # Here we try to match it with a siret in offerer's managed venues
    if PreBusinessUnitStatus.DRAFT_API_SIRET_NOT_MATCH in status_to_process:
        builder.process_draft_api_siret_not_match()

    # We found the offerer main SIRET in offerer's mannaged venues
    # Here we check that it's not already part of a BusinessUnit or PreBusinessUnit
    if PreBusinessUnitStatus.DRAFT_API_SIRET_MATCH_MANAGED_VENUES in status_to_process:
        builder.process_draft_api_siret_match_managed_venues()

    # The main SIRET doesn't exist on offerer's managed venue
    # Here we try to match main venue address within PreBusinessUnit venues
    if PreBusinessUnitStatus.DRAFT_API_SIRET_NOT_MATCH_MANAGED_VENUE in status_to_process:
        builder.process_draft_api_siret_not_match_managed_venue()

    # Main venue have been found in PreBusinessUnit venue by matching the address.
    # Here we assign main the main SIRET to this venue
    if PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH in status_to_process:
        builder.process_pending_api_address_match()

    # The main SIRET doesn't exist on offerer's managed venue
    # and the main address doesn't match any of the PreBusinessUnit venues
    # Here we try to match the address within offerer's managed venues
    if PreBusinessUnitStatus.DRAFT_API_ADDRESS_NOT_MATCH in status_to_process:
        builder.process_draft_api_address_not_match()

    # Main venue have been found in offerer's managed venues by matching the address.
    # Here we assign main the main SIRET to this venue and append it to the PreBusinessUnit
    if PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE in status_to_process:
        builder.process_pending_api_address_match_managed_venue()

    # The main venue haven't been found with neither SIRET or address match
    # Here we create a new venue from "siren api" data and append it to the PreBusinessUnit
    if PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE in status_to_process:
        builder.process_pending_api_address_not_match_managed_venue()

    ready_status_to_process = list(set(PRE_BUSINESS_UNIT_READY_STATUS) & set(status_to_process))
    if len(ready_status_to_process) > 0:
        builder.process_ready(ready_status_to_process)


def process_all_offerers(status_to_process=None, offererIsActive=True):
    pre_business_unit_report = PreBusinessUnitReport()
    active_offerers = Offerer.query.filter(Offerer.isActive == offererIsActive).order_by(Offerer.id).all()

    for offerer in active_offerers:
        builder = OffererBusinessUnitBuilder(offerer)
        builder.build_pre_business_units()
        if status_to_process:
            process_statuses(builder, status_to_process)
        pre_business_unit_report.add_offerer_pre_business_units(offerer.id, builder.pre_business_units)
    return pre_business_unit_report
