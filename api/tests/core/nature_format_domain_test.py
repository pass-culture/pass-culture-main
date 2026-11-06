from pcapi.core.nature_format_domain import nature_format_domain


def test_fields_bien_has_all_formats():
    assert set(nature_format_domain.FIELDS_BIEN) == set(nature_format_domain.FormatEnum)
