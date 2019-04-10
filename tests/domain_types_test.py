import pytest

from domain.types import get_formatted_event_or_thing_types, get_event_or_thing_type_values_from_sublabels


class GetFormattedEventOrThingTypesTest:
    @pytest.mark.standalone
    def test_returns_all_types_except_activations_if_user_is_not_admin(self):
        # when
        types = get_formatted_event_or_thing_types(with_activation_type=False)

        # then
        assert types[0] == {
            'conditionalFields': ["author", "visa", "stageDirector"],
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
        assert len(types) == 17

    @pytest.mark.standalone
    def test_returns_all_types_including_activations_if_user_is_admin(self):
        # given
        activation_event = {
            'conditionalFields': [],
            'offlineOnly': True,
            'onlineOnly': False,
            'sublabel': 'Activation',
            'type': 'Event',
            'value': 'EventType.ACTIVATION',
            'description': 'Activez votre pass Culture grâce à cette offre',
            'label': 'Pass Culture : activation évènementielle'
        }

        activation_thing = {
            'conditionalFields': [],
            'type': 'Thing',
            'value': 'ThingType.ACTIVATION',
            'label': 'Pass Culture : activation en ligne',
            'offlineOnly': False,
            'onlineOnly': True,
            'sublabel': 'Activation',
            'description': 'Activez votre pass Culture grâce à cette offre'
        }

        # when
        types = get_formatted_event_or_thing_types(with_activation_type=True)

        # then
        assert activation_event in types
        assert activation_thing in types
        assert len(types) == 19

    @pytest.mark.standalone
    def test_does_not_return_thing_type_jeux(self):
        # given
        jeux = {
            'conditionalFields': [],
            'type': 'Thing',
            'value': 'ThingType.JEUX',
            'label': "Jeux (Biens physiques)",
            'offlineOnly': True,
            'onlineOnly': False,
            'sublabel': "Jouer",
            'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?"
        }

        # when
        types = get_formatted_event_or_thing_types(with_activation_type=False)

        # then
        assert jeux not in types, 'Les offres avec le type "ThingType.JEUX" ne peuvent plus être créées pour être en ' \
                                  'phase avec les CGU'


@pytest.mark.standalone
def test_get_event_or_thing_type_values_from_sublabels():
    # given
    type_values = get_event_or_thing_type_values_from_sublabels('Rencontrer')

    # then
    assert type_values[0] == 'EventType.CONFERENCE_DEBAT_DEDICACE'
