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
