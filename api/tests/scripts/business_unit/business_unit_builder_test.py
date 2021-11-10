from copy import deepcopy
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.factories import OffererFactory
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.factories import BankInformationFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.bank_information import BankInformation
from pcapi.scripts.business_unit.business_unit_builder import PRE_BUSINESS_UNIT_DRAFT_STATUS
from pcapi.scripts.business_unit.business_unit_builder import PRE_BUSINESS_UNIT_PENDING_STATUS
from pcapi.scripts.business_unit.business_unit_builder import PRE_BUSINESS_UNIT_READY_STATUS
from pcapi.scripts.business_unit.business_unit_builder import PRE_BUSINESS_UNIT_REPORT_STATUS
from pcapi.scripts.business_unit.business_unit_builder import PreBusinessUnitStatus
from pcapi.scripts.business_unit.business_unit_builder import process_all_offerers


def print_report_count_by_status(report):
    print("###")
    for st in report:
        if len(report[st]["offerer_ids"]) > 0 or len(report[st]["venue_ids"]) > 0:
            print("status", st)
            print("nb_offerers", len(report[st]["offerer_ids"]))
            print("offerer_ids", report[st]["offerer_ids"])
            print("nb_venues", len(report[st]["venue_ids"]))
            print("venue_ids", report[st]["venue_ids"])
            print("---")
    print("###")


def create_venues(offerer, with_siret=True, bank_information=True):
    venue_data = {
        "managingOfferer": offerer,
        "businessUnit": None,
    }
    if not with_siret:
        venue_data["siret"] = None
        venue_data["comment"] = "no siret"

    bank_information_list = []
    venue = VenueFactory(**venue_data)
    if bank_information and not isinstance(bank_information, BankInformation):
        bank_information = BankInformationFactory(venue=venue)
        bank_information_list.append(bank_information)
    venue_list = [venue, VenueFactory(**venue_data)]
    if bank_information:
        for v in venue_list:
            if not v.bankInformation:
                bank_information_list.append(
                    BankInformationFactory(venue=v, bic=bank_information.bic, iban=bank_information.iban)
                )
    return {
        "venues": venue_list,
        "bank_informations": bank_information_list,
    }


def create_offerer():
    data = {
        "offerer": OffererFactory(),
        "pre_business_units": {
            "one_siret": {},
            "too_many_siret": {},
            "no_siret": {},
        },
    }

    # some unused data, these should not be part of any business unit
    create_venues(data["offerer"], with_siret=True, bank_information=False)
    create_venues(data["offerer"], with_siret=False, bank_information=False)

    # pre_bu with one siret
    pre_bu = {}
    pre_bu["main_venue"] = VenueFactory(managingOfferer=data["offerer"], businessUnit=None)
    pre_bu["main_bank_information"] = BankInformationFactory(venue=pre_bu["main_venue"])
    created_venues = create_venues(data["offerer"], with_siret=False, bank_information=pre_bu["main_bank_information"])
    pre_bu["venues"] = [
        pre_bu["main_venue"],
        *created_venues["venues"],
    ]
    pre_bu["bank_informations"] = [pre_bu["main_bank_information"], *created_venues["bank_informations"]]
    data["pre_business_units"]["one_siret"] = pre_bu

    # pre_bu with too many siret
    pre_bu = {}
    pre_bu["main_venue"] = VenueFactory(managingOfferer=data["offerer"], businessUnit=None)
    pre_bu["main_bank_information"] = BankInformationFactory(venue=pre_bu["main_venue"])
    created_venues = create_venues(data["offerer"], with_siret=True, bank_information=pre_bu["main_bank_information"])
    pre_bu["venues"] = [
        pre_bu["main_venue"],
        *created_venues["venues"],
    ]
    pre_bu["bank_informations"] = [pre_bu["main_bank_information"], *created_venues["bank_informations"]]
    data["pre_business_units"]["too_many_siret"] = pre_bu

    # pre_bu with no siret
    pre_bu = {}
    pre_bu["main_venue"] = VenueFactory(
        managingOfferer=data["offerer"],
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    pre_bu["main_bank_information"] = BankInformationFactory(venue=pre_bu["main_venue"])
    created_venues = create_venues(data["offerer"], with_siret=False, bank_information=pre_bu["main_bank_information"])
    pre_bu["venues"] = [
        pre_bu["main_venue"],
        *created_venues["venues"],
    ]
    pre_bu["bank_informations"] = [pre_bu["main_bank_information"], *created_venues["bank_informations"]]
    data["pre_business_units"]["no_siret"] = pre_bu

    return data


def get_api_response(
    siren, venue_data={"siret": None, "name": None, "address": None, "postalCode": None, "city": None}
):
    main_venue_api_data = {
        "code_postal": "46500",
        "enseigne_1": "DEFAULT_ENSEIGNE_1",
        "geo_adresse": "DEFAULT_GEO_ADDRESSE",
        "geo_l4": "DEFAULT_GEO_L4",
        "geo_l5": None,
        "code_postal": "DEFAULT_POSTAL_CODE",
        "latitude": "44.779352",
        "libelle_commune": "DEFAULT_LIBELLE_COMMUNE",
        "longitude": "1.723758",
        "numero_voie": "DEFAULT_LATITUDE",
        "siren": siren,
        "siret": "DEFAULT_SIRET",
        "type_voie": "PL",
    }
    if "siret" in venue_data:
        main_venue_api_data["siret"] = venue_data["siret"]
    if "name" in venue_data:
        main_venue_api_data["enseigne_1"] = venue_data["name"]
    if "address" in venue_data:
        main_venue_api_data["geo_l4"] = venue_data["address"]
    if "postalCode" in venue_data:
        main_venue_api_data["code_postal"] = venue_data["postalCode"]
    if "city" in venue_data:
        main_venue_api_data["libelle_commune"] = venue_data["city"]

    response = {
        "unite_legale": {
            "etablissement_siege": main_venue_api_data,
            "etablissements": [],
            "etat_administratif": "A",
            "id": 226257595,
            "identifiant_association": None,
            "nic_siege": "00068",
            "nom": None,
            "nom_usage": None,
            "nombre_periodes": "7",
            "nomenclature_activite_principale": "NAFRev2",
            "numero_tva_intra": "FR35214601288",
            "prenom_1": None,
            "prenom_2": None,
            "prenom_3": None,
            "prenom_4": None,
            "prenom_usuel": None,
            "pseudonyme": None,
            "sexe": None,
            "sigle": None,
            "siren": "214601288",
            "statut_diffusion": "O",
            "tranche_effectifs": "21",
            "unite_purgee": None,
            "updated_at": "2021-08-03T02:01:36.835+02:00",
        }
    }

    return response


def get_api_response_mock(
    siren, venue_data={"siret": None, "name": None, "address": None, "postalCode": None, "city": None}
):
    return MagicMock(
        status_code=200,
        text="",
        json=MagicMock(
            return_value=get_api_response(siren, venue_data),
        ),
    )


class AutoFillBusinessUnitSiretTest:
    @pytest.mark.usefixtures("db_session")
    def test_report_structure(self):
        pre_business_unit_report = process_all_offerers()
        report = pre_business_unit_report.report

        assert sorted(list(report.keys())) == sorted(PRE_BUSINESS_UNIT_REPORT_STATUS)

        for status_report in report.values():
            assert sorted(list(status_report.keys())) == sorted(
                [
                    "venue_ids",
                    "offerer_ids",
                    "nb_pre_business_unit",
                    "pre_business_unit_ids",
                ]
            )
        for status in report.keys():
            assert len(report[status]["offerer_ids"]) == 0
            assert len(report[status]["venue_ids"]) == 0
            assert len(report[status]["pre_business_unit_ids"]) == 0
            assert report[status]["nb_pre_business_unit"] == 0

    @pytest.mark.usefixtures("db_session")
    def test_ready(self):
        test_data = create_offerer()
        expected_report_data = {
            PreBusinessUnitStatus.READY: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]]),
            },
            PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted(
                    [
                        *[v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]],
                        *[v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
                    ]
                ),
            },
        }

        pre_business_unit_report = process_all_offerers()
        report = pre_business_unit_report.report

        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["venue_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET]["venue_ids"]
        )

    @pytest.mark.usefixtures("db_session")
    def test_created(self):
        test_data = create_offerer()

        expected_created_venues = test_data["pre_business_units"]["one_siret"]["venues"]
        expected_main_siret = test_data["pre_business_units"]["one_siret"]["main_venue"].siret
        expected_main_bank_information = test_data["pre_business_units"]["one_siret"]["main_venue"].bankInformation
        expected_report_data = {
            PreBusinessUnitStatus.READY: {
                "offerer_ids": [],
                "venue_ids": [],
            },
            PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted(
                    [
                        *[v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]],
                        *[v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
                    ]
                ),
            },
            PreBusinessUnitStatus.CREATED: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in expected_created_venues]),
            },
        }

        pre_business_unit_report = process_all_offerers(PRE_BUSINESS_UNIT_READY_STATUS)
        report = pre_business_unit_report.report

        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["venue_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.DRAFT_NO_MAIN_SIRET]["venue_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 1

        business_unit = business_units[0]
        assert business_unit.siret == expected_main_siret
        assert business_unit.bankAccountId == expected_main_bank_information.id
        for venue in expected_created_venues:
            assert venue.businessUnitId == business_unit.id

    @patch("pcapi.connectors.api_entreprises.requests.get")
    @pytest.mark.usefixtures("db_session")
    def test_pending_api_address_not_match_managed_venue(self, mock_api_entreprise):
        """
        -> PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE,
            -> PreBusinessUnitStatus.READY_MAIN_VENUE_CREATED
            -> PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
        PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH,
        PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE,

        PreBusinessUnitStatus.READY,
        PreBusinessUnitStatus.READY_API_SIRET_MATCH,
        PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE,

        PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
        """

        test_data = create_offerer()
        mock_api_entreprise.side_effect = [
            get_api_response_mock(test_data["offerer"].siren, venue_data={"siret": "NOT FOUND"}),
        ]
        expected_report_data = {
            PreBusinessUnitStatus.READY: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]]),
            },
            PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": [
                    *[v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]],
                    *[v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
                ],
            },
        }
        pre_business_unit_report = process_all_offerers(PRE_BUSINESS_UNIT_DRAFT_STATUS)
        report = pre_business_unit_report.report

        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["venue_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 0

        # Then when we process pending status, main venue should be create

        main_venue_siret = f'{test_data["offerer"].siren}11111'
        mock_api_entreprise.side_effect = [
            get_api_response_mock(
                test_data["offerer"].siren,
                venue_data={
                    "siret": main_venue_siret,
                    "address": "main venue address",
                    "postalCode": "93000",
                    "city": "main venue city",
                },
            ),
        ]
        expected_report_data = {
            PreBusinessUnitStatus.READY_MAIN_VENUE_CREATED: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": [
                    *[v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]],
                ],
            },
            PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": [
                    *[v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
                ],
            },
        }
        pre_business_unit_report = process_all_offerers(
            [
                *PRE_BUSINESS_UNIT_DRAFT_STATUS,
                *PRE_BUSINESS_UNIT_PENDING_STATUS,
            ]
        )
        report = pre_business_unit_report.report
        main_venue = Venue.query.filter(Venue.siret == main_venue_siret).one_or_none()
        assert isinstance(main_venue, Venue)
        assert main_venue.address == "main venue address"
        assert main_venue.postalCode == "93000"
        assert main_venue.city == "main venue city"
        expected_report_data[PreBusinessUnitStatus.READY_MAIN_VENUE_CREATED]["venue_ids"].append(main_venue.id)

        assert (
            sorted(list(report[PreBusinessUnitStatus.READY_MAIN_VENUE_CREATED]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY_MAIN_VENUE_CREATED]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY_MAIN_VENUE_CREATED]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY_MAIN_VENUE_CREATED]["venue_ids"]
        )
        assert (
            sorted(
                list(report[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["offerer_ids"])
            )
            == expected_report_data[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "offerer_ids"
            ]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "venue_ids"
            ]
        )

        # Then when we process ready status, BusinessUnit should be created
        expected_report_data = {
            PreBusinessUnitStatus.CREATED: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted(
                    [
                        main_venue.id,
                        *[v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]],
                        *[v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]],
                    ]
                ),
            },
            PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted(
                    [
                        *[v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
                    ]
                ),
            },
        }
        mock_api_entreprise.side_effect = [
            get_api_response_mock(
                test_data["offerer"].siren,
                venue_data={
                    "siret": main_venue_siret,
                    "address": "main venue address",
                    "postalCode": "93000",
                    "city": "main venue city",
                },
            ),
        ]
        pre_business_unit_report = process_all_offerers(
            [
                *PRE_BUSINESS_UNIT_DRAFT_STATUS,
                *PRE_BUSINESS_UNIT_PENDING_STATUS,
                *PRE_BUSINESS_UNIT_READY_STATUS,
            ]
        )
        report = pre_business_unit_report.report
        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 2

    @patch("pcapi.connectors.api_entreprises.requests.get")
    @pytest.mark.usefixtures("db_session")
    def test_ready_api_siret_match(self, mock_api_entreprise):
        """
        -> PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE,
        -> PreBusinessUnitStatus.READY_API_SIRET_MATCH,

        PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH,
        PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE,

        PreBusinessUnitStatus.READY,
        PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE,

        -> PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
        PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
        """
        test_data = create_offerer()
        main_venue = test_data["pre_business_units"]["too_many_siret"]["main_venue"]
        mock_api_entreprise.side_effect = [
            get_api_response_mock(test_data["offerer"].siren, venue_data={"siret": main_venue.siret}),
        ]
        expected_report_data = {
            PreBusinessUnitStatus.READY: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]]),
            },
            PreBusinessUnitStatus.READY_API_SIRET_MATCH: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]]),
            },
            PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": [
                    *[v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
                ],
            },
        }

        pre_business_unit_report = process_all_offerers(PRE_BUSINESS_UNIT_DRAFT_STATUS)
        report = pre_business_unit_report.report

        assert (
            sorted(list(report[PreBusinessUnitStatus.READY_API_SIRET_MATCH]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY_API_SIRET_MATCH]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY_API_SIRET_MATCH]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY_API_SIRET_MATCH]["venue_ids"]
        )

        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["venue_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "offerer_ids"
            ]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 0

        # Then on process ready BusinessUnit should be created
        mock_api_entreprise.side_effect = [
            get_api_response_mock(test_data["offerer"].siren, venue_data={"siret": main_venue.siret}),
        ]
        expected_report_data = {
            PreBusinessUnitStatus.CREATED: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted(
                    [
                        *[v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]],
                        *[v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]],
                    ]
                ),
            },
            PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": [
                    *[v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
                ],
            },
        }
        pre_business_unit_report = process_all_offerers(
            [*PRE_BUSINESS_UNIT_DRAFT_STATUS, *PRE_BUSINESS_UNIT_READY_STATUS]
        )
        report = pre_business_unit_report.report
        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["venue_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "offerer_ids"
            ]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 2

    @patch("pcapi.connectors.api_entreprises.requests.get")
    @pytest.mark.usefixtures("db_session")
    def test_process_draft_api_siret_match_managed_venues(self, mock_api_entreprise):
        """
        -> PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE,
        -> PreBusinessUnitStatus.READY_API_SIRET_MATCH,
        -> PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE,

        PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH,
        PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE,

        PreBusinessUnitStatus.READY,

        -> PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
        PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
        """
        test_data = create_offerer()
        main_managed_venue = VenueFactory(managingOfferer=test_data["offerer"], businessUnit=None)
        mock_api_entreprise.side_effect = [
            get_api_response_mock(test_data["offerer"].siren, venue_data={"siret": main_managed_venue.siret}),
        ]
        expected_report_data = {
            PreBusinessUnitStatus.READY: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]]),
            },
            PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted(
                    [
                        main_managed_venue.id,
                        *[v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]],
                    ]
                ),
            },
            PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": [
                    *[v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
                ],
            },
        }

        pre_business_unit_report = process_all_offerers(PRE_BUSINESS_UNIT_DRAFT_STATUS)
        report = pre_business_unit_report.report

        assert (
            sorted(list(report[PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE]["venue_ids"]
        )

        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["venue_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "offerer_ids"
            ]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 0

        # Then on process ready BusinessUnit should be created
        mock_api_entreprise.side_effect = [
            get_api_response_mock(test_data["offerer"].siren, venue_data={"siret": main_managed_venue.siret}),
        ]
        expected_report_data = {
            PreBusinessUnitStatus.CREATED: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted(
                    [
                        main_managed_venue.id,
                        *[v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]],
                        *[v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]],
                    ]
                ),
            },
            PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": [
                    *[v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
                ],
            },
        }

        pre_business_unit_report = process_all_offerers(
            [*PRE_BUSINESS_UNIT_DRAFT_STATUS, *PRE_BUSINESS_UNIT_READY_STATUS]
        )
        report = pre_business_unit_report.report

        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["venue_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "offerer_ids"
            ]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 2

    @patch("pcapi.connectors.api_entreprises.requests.get")
    @pytest.mark.usefixtures("db_session")
    def test_pending_address_match(self, mock_api_entreprise):
        """
        -> PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE,
        -> PreBusinessUnitStatus.READY_API_SIRET_MATCH,
        -> PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE,
        -> PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH,
            -> READY_API_ADDRESS_MATCH

        PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE,

        PreBusinessUnitStatus.READY,

        PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
        -> PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
        """
        test_data = create_offerer()
        main_venue = test_data["pre_business_units"]["no_siret"]["main_venue"]
        main_venue.address = "match address"
        main_venue.postalCode = "93000"
        main_venue.city = "match city"
        main_venue_siret = f'{test_data["offerer"].siren}11111'
        mock_api_entreprise.side_effect = [
            get_api_response_mock(
                test_data["offerer"].siren,
                venue_data={
                    "siret": main_venue_siret,
                    "address": main_venue.address,
                    "postalCode": main_venue.postalCode,
                    "city": main_venue.city,
                },
            ),
        ]

        expected_report_data = {
            PreBusinessUnitStatus.READY: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]]),
            },
            PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": [v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
            },
            PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]]),
            },
        }

        pre_business_unit_report = process_all_offerers(PRE_BUSINESS_UNIT_DRAFT_STATUS)
        report = pre_business_unit_report.report

        assert (
            sorted(list(report[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH]["venue_ids"]
        )

        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["venue_ids"]
        )
        assert (
            sorted(
                list(report[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["offerer_ids"])
            )
            == expected_report_data[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "offerer_ids"
            ]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "venue_ids"
            ]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 0

        # if we also process PENDING_API_ADDRESS_MATCH, status should be change to READY_API_ADDRESS_MATCH
        main_venue_siret = f'{test_data["offerer"].siren}11111'
        mock_api_entreprise.side_effect = [
            get_api_response_mock(
                test_data["offerer"].siren,
                venue_data={
                    "siret": main_venue_siret,
                    "address": main_venue.address,
                    "postalCode": main_venue.postalCode,
                    "city": main_venue.city,
                },
            ),
        ]
        pre_business_unit_report = process_all_offerers(
            [
                *PRE_BUSINESS_UNIT_DRAFT_STATUS,
                *PRE_BUSINESS_UNIT_PENDING_STATUS,
            ]
        )
        report = pre_business_unit_report.report

        assert len(list(report[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH]["offerer_ids"])) == 0
        assert len(list(report[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH]["venue_ids"])) == 0
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY_API_ADDRESS_MATCH]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY_API_ADDRESS_MATCH]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 0

        main_venue = Venue.query.get(main_venue.id)
        assert main_venue.siret == main_venue_siret

        # Then on process ready BusinessUnit should be created
        expected_report_data = {
            PreBusinessUnitStatus.CREATED: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted(
                    [
                        *[v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]],
                        *[v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]],
                    ]
                ),
            },
            PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]]),
            },
        }
        mock_api_entreprise.side_effect = [
            get_api_response_mock(
                test_data["offerer"].siren,
                venue_data={
                    "siret": main_venue_siret,
                    "address": main_venue.address,
                    "postalCode": main_venue.postalCode,
                    "city": main_venue.city,
                },
            ),
        ]
        pre_business_unit_report = process_all_offerers(
            [
                *PRE_BUSINESS_UNIT_DRAFT_STATUS,
                *PRE_BUSINESS_UNIT_PENDING_STATUS,
                *PRE_BUSINESS_UNIT_READY_STATUS,
            ]
        )
        report = pre_business_unit_report.report

        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["venue_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "offerer_ids"
            ]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 2

    @patch("pcapi.connectors.api_entreprises.requests.get")
    @pytest.mark.usefixtures("db_session")
    def test_process_draft_api_address_not_match(self, mock_api_entreprise):
        """
        -> PreBusinessUnitStatus.PENDING_API_ADDRESS_NOT_MATCH_MANAGED_VENUE,
        -> PreBusinessUnitStatus.READY_API_SIRET_MATCH,
        -> PreBusinessUnitStatus.READY_API_SIRET_MATCH_MANAGED_VENUE,
        -> PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH,
            -> READY_API_ADDRESS_MATCH

        PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE,

        PreBusinessUnitStatus.READY,

        PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
        -> PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE,
        """
        test_data = create_offerer()
        main_venue = VenueFactory(
            managingOfferer=test_data["offerer"],
            businessUnit=None,
            address="match address",
            postalCode="93000",
            city="match city",
            siret=None,
            comment="no siret",
        )
        main_venue_siret = f'{test_data["offerer"].siren}11111'
        mock_api_entreprise.side_effect = [
            get_api_response_mock(
                test_data["offerer"].siren,
                venue_data={
                    "siret": main_venue_siret,
                    "address": main_venue.address,
                    "postalCode": main_venue.postalCode,
                    "city": main_venue.city,
                },
            ),
        ]

        expected_report_data = {
            PreBusinessUnitStatus.READY: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]]),
            },
            PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted(
                    [main_venue.id, *[v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]]]
                ),
            },
            PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]]),
            },
        }

        pre_business_unit_report = process_all_offerers(PRE_BUSINESS_UNIT_DRAFT_STATUS)
        report = pre_business_unit_report.report

        assert (
            sorted(list(report[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE]["venue_ids"]
        )

        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.READY]["venue_ids"]
        )
        assert (
            sorted(
                list(report[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["offerer_ids"])
            )
            == expected_report_data[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "offerer_ids"
            ]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_ADDRESS_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "venue_ids"
            ]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 0

        # if we also process PENDING_API_ADDRESS_MATCH, status should be change to READY_API_ADDRESS_MATCH
        main_venue_siret = f'{test_data["offerer"].siren}11111'
        mock_api_entreprise.side_effect = [
            get_api_response_mock(
                test_data["offerer"].siren,
                venue_data={
                    "siret": main_venue_siret,
                    "address": main_venue.address,
                    "postalCode": main_venue.postalCode,
                    "city": main_venue.city,
                },
            ),
        ]
        pre_business_unit_report = process_all_offerers(
            [
                *PRE_BUSINESS_UNIT_DRAFT_STATUS,
                *PRE_BUSINESS_UNIT_PENDING_STATUS,
            ]
        )
        report = pre_business_unit_report.report

        assert len(list(report[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE]["offerer_ids"])) == 0
        assert len(list(report[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE]["venue_ids"])) == 0
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY_API_ADDRESS_MATCH_MANAGED_VENUE]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.READY_API_ADDRESS_MATCH_MANAGED_VENUE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.PENDING_API_ADDRESS_MATCH_MANAGED_VENUE]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 0

        main_venue = Venue.query.get(main_venue.id)
        assert main_venue.siret == main_venue_siret

        # Then on process ready BusinessUnit should be created
        mock_api_entreprise.side_effect = [
            get_api_response_mock(
                test_data["offerer"].siren,
                venue_data={
                    "siret": main_venue_siret,
                    "address": main_venue.address,
                    "postalCode": main_venue.postalCode,
                    "city": main_venue.city,
                },
            ),
        ]
        expected_report_data = {
            PreBusinessUnitStatus.CREATED: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted(
                    [
                        main_venue.id,
                        *[v.id for v in test_data["pre_business_units"]["too_many_siret"]["venues"]],
                        *[v.id for v in test_data["pre_business_units"]["one_siret"]["venues"]],
                    ]
                ),
            },
            PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE: {
                "offerer_ids": [test_data["offerer"].id],
                "venue_ids": sorted([v.id for v in test_data["pre_business_units"]["no_siret"]["venues"]]),
            },
        }
        pre_business_unit_report = process_all_offerers(
            [
                *PRE_BUSINESS_UNIT_DRAFT_STATUS,
                *PRE_BUSINESS_UNIT_PENDING_STATUS,
                *PRE_BUSINESS_UNIT_READY_STATUS,
            ]
        )
        report = pre_business_unit_report.report
        print_report_count_by_status(report)

        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["offerer_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.CREATED]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.CREATED]["venue_ids"]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["offerer_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE][
                "offerer_ids"
            ]
        )
        assert (
            sorted(list(report[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]))
            == expected_report_data[PreBusinessUnitStatus.END_API_SIRET_MATCH_MANAGED_VENUE_NOT_ASSIGNABLE]["venue_ids"]
        )

        business_units = BusinessUnit.query.all()
        assert len(business_units) == 2
