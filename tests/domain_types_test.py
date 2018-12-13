import pytest

from domain.types import get_formatted_event_or_thing_types, get_event_or_thing_type_values_from_sublabels


@pytest.mark.standalone
def test_get_formatted_event_or_thing_types_returns_all_types_except_activations_if_user_is_not_admin():
    # when
    types = get_formatted_event_or_thing_types(with_activation_type=False)

    # then
    assert types[0] == {
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': 'Regarder',
        'type': 'Event',
        'value': 'EventType.CINEMA',
        'description': 'Action, science-fiction, documentaire ou comédie sentimentale '
                       '? En salle, en plein air ou bien au chaud chez soi ? Et si '
                       'c’était plutôt cette exposition qui allait faire son cinéma ?',
        'label': 'Cinéma (Projections, Séances, Évènements)'
    }
    assert len(types) == 18


@pytest.mark.standalone
def test_get_formatted_event_or_thing_types_returns_all_types_including_activations_if_user_is_admin():
    # given
    activation_event = {
        'offlineOnly': True,
        'onlineOnly': False,
        'sublabel': 'Activation',
        'type': 'Event',
        'value': 'EventType.ACTIVATION',
        'description': 'Activez votre pass Culture grâce à cette offre',
        'label': 'Activation événementielle du pass Culture'
    }

    # when
    types = get_formatted_event_or_thing_types(with_activation_type=True)

    # then
    assert activation_event in types
    assert len(types) == 19


@pytest.mark.standalone
def test_get_event_or_thing_type_values_from_sublabels():
    # given
    type_values = get_event_or_thing_type_values_from_sublabels('Rencontrer')

    # then
    assert type_values[0] == 'EventType.CONFERENCE_DEBAT_DEDICACE'
