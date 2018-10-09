import pytest

from domain.types import get_format_types, get_type_values_from_sublabels


@pytest.mark.standalone
def test_get_format_types():
    # given
    types = get_format_types()

    # then
    assert types[0]['label'] == 'Cinéma (Projections, Séances, Évènements)'

@pytest.mark.standalone
def test_get_type_values_from_sublabels():
    # given
    type_values = get_type_values_from_sublabels('Rencontrer')

    # then
    assert type_values[0] == 'EventType.CONFERENCE_DEBAT_DEDICACE'
