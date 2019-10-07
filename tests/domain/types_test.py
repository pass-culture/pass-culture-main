from domain.types import get_formatted_active_product_types, get_active_product_type_values_from_sublabels


class GetFormattedEventOrThingTypesTest:
    def test_returns_all_types_except_activations_if_user_is_not_admin(self):
        # when
        types = get_formatted_active_product_types(with_activation_type=False)

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
            'proLabel': 'Cinéma - projections et autres évènements',
            'appLabel': 'Cinéma',
            'isActive': True
        }
        assert len(types) == 21

    def test_returns_all_types_including_activations_if_user_is_admin(self):
        # given
        activation_event_product = {
            'conditionalFields': [],
            'offlineOnly': True,
            'onlineOnly': False,
            'sublabel': 'Activation',
            'type': 'Event',
            'value': 'EventType.ACTIVATION',
            'description': 'Activez votre pass Culture grâce à cette offre',
            'proLabel': 'Pass Culture : activation évènementielle',
            'appLabel': 'Pass Culture : activation évènementielle',
            'isActive': True
        }

        activation_thing_product = {
            'conditionalFields': [],
            'type': 'Thing',
            'value': 'ThingType.ACTIVATION',
            'proLabel': 'Pass Culture : activation en ligne',
            'appLabel': "Pass Culture : activation en ligne",
            'offlineOnly': False,
            'onlineOnly': True,
            'sublabel': 'Activation',
            'description': 'Activez votre pass Culture grâce à cette offre',
            'isActive': True
        }

        # when
        types = get_formatted_active_product_types(with_activation_type=True)

        # then
        assert activation_event_product in types
        assert activation_thing_product in types
        assert len(types) == 23

    def test_does_not_return_inactive_product_types(self):
        # given
        jeux = {
            'conditionalFields': [],
            'type': 'Thing',
            'value': 'ThingType.JEUX',
            'proLabel': "Jeux (support physique)",
            'offlineOnly': True,
            'onlineOnly': False,
            'sublabel': "Jouer",
            'description': "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
            'isActive': False
        }

        # when
        types = get_formatted_active_product_types(with_activation_type=False)

        # then
        assert jeux not in types, 'Les offres avec le type "ThingType.JEUX" ne peuvent plus être créées pour être en ' \
                                  'phase avec les CGU'


def test_get_active_product_type_values_from_sublabels():
    # given
    type_values = get_active_product_type_values_from_sublabels('Rencontrer')

    # then
    assert type_values[0] == 'EventType.CONFERENCE_DEBAT_DEDICACE'
