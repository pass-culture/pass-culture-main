from pcapi.core.nature_format_domain import FieldEnum
from pcapi.core.nature_format_domain import FormatEnum
from pcapi.core.nature_format_domain import NatureEnum
from pcapi.core.nature_format_domain import get_capabilities
from pcapi.core.nature_format_domain import get_mandatory_fields
from pcapi.core.nature_format_domain import nature_format_domain


def test_fields_bien_has_all_bien_formats():
    bien_formats = {
        format_["format"]
        for nature in nature_format_domain.NFD
        if nature["nature"] == nature_format_domain.NatureEnum.BIEN
        for format_ in nature["formats"]
    }

    assert set(nature_format_domain.FIELDS_BIEN) == bien_formats


def test_nfd_contains_all_natures():
    natures = {nature["nature"] for nature in nature_format_domain.NFD}
    missing_natures = set(nature_format_domain.NatureEnum) - natures

    assert not missing_natures


def test_nfd_contains_all_formats():
    formats = {format_["format"] for nature in nature_format_domain.NFD for format_ in nature["formats"]}
    missing_formats = set(nature_format_domain.FormatEnum) - formats

    assert not missing_formats


def test_nfd_contains_all_domains():
    domains = {
        domain["domain"]
        for nature in nature_format_domain.NFD
        for format_ in nature["formats"]
        for domain in format_.get("domains", [])
    }
    missing_domains = set(nature_format_domain.DomainEnum) - domains

    assert not missing_domains


def test_get_capabilities_bien():
    capabilities = get_capabilities(NatureEnum.BIEN, FormatEnum.CD)
    assert FieldEnum.TITLE_BIEN in capabilities
    assert FieldEnum.PRICE in capabilities


def test_get_capabilities_evenement():
    capabilities = get_capabilities(NatureEnum.EVENEMENT, FormatEnum.CONCERT)
    assert FieldEnum.TITLE in capabilities
    assert FieldEnum.START_DATE in capabilities


def test_get_capabilities_carte_no_refund_domain():
    capabilities = get_capabilities(NatureEnum.CARTE_ABONNEMENT, FormatEnum.CARTE, domain="VOD")
    assert FieldEnum.DIGITAL_COMPULSORY in capabilities


def test_get_capabilities_carte_refund_domain():
    capabilities = get_capabilities(NatureEnum.CARTE_ABONNEMENT, FormatEnum.CARTE, domain="CINEMA")
    assert FieldEnum.WITHDRAWAL_TYPES in capabilities


def test_get_capabilities_carte_no_domain():
    capabilities = get_capabilities(NatureEnum.CARTE_ABONNEMENT, FormatEnum.CARTE)
    assert FieldEnum.DIGITAL_COMPULSORY not in capabilities


def test_get_mandatory_fields_bien():
    mandatory = get_mandatory_fields(NatureEnum.BIEN, FormatEnum.CD)
    assert FieldEnum.TITLE in mandatory


def test_get_mandatory_fields_carte_no_refund_domain():
    mandatory = get_mandatory_fields(NatureEnum.CARTE_ABONNEMENT, FormatEnum.CARTE, domain="VOD")
    assert FieldEnum.DIGITAL_COMPULSORY in mandatory


def test_get_mandatory_fields_carte_refund_domain():
    mandatory = get_mandatory_fields(NatureEnum.CARTE_ABONNEMENT, FormatEnum.CARTE, domain="CINEMA")
    assert FieldEnum.WITHDRAWAL_TYPES in mandatory
