from pcapi.domain.types import get_active_product_type_values_from_sublabels
from pcapi.domain.types import get_formatted_active_product_types


class GetFormattedEventOrThingTypesTest:
    def test_returns_all_types_except_activations(self):
        # when
        types = get_formatted_active_product_types()

        # then
        assert types[0] == {
            "conditionalFields": ["author", "visa", "stageDirector"],
            "offlineOnly": True,
            "onlineOnly": False,
            "sublabel": "Regarder",
            "type": "Event",
            "value": "EventType.CINEMA",
            "description": "Action, science-fiction, documentaire ou comédie sentimentale "
            "? En salle, en plein air ou bien au chaud chez soi ? Et si "
            "c’était plutôt cette exposition qui allait faire son cinéma ?",
            "proLabel": "Cinéma - projections et autres évènements",
            "appLabel": "Cinéma",
            "isActive": True,
        }
        assert len(types) == 22

    def test_does_not_return_inactive_product_types(self):
        # given
        jeux = {
            "conditionalFields": [],
            "type": "Thing",
            "value": "ThingType.JEUX",
            "proLabel": "Jeux (support physique)",
            "offlineOnly": True,
            "onlineOnly": False,
            "sublabel": "Jouer",
            "description": "Résoudre l’énigme d’un jeu de piste dans votre ville ? Jouer en ligne entre amis ? Découvrir cet univers étrange avec une manette ?",
            "isActive": False,
        }

        # when
        types = get_formatted_active_product_types()

        # then
        assert (
            jeux not in types
        ), 'Les offres avec le type "ThingType.JEUX" ne peuvent plus être créées pour être en phase avec les CGU'


def test_get_active_product_type_values_from_sublabels():
    # given
    type_values = get_active_product_type_values_from_sublabels("Rencontrer")

    # then
    assert type_values[0] == "EventType.CONFERENCE_DEBAT_DEDICACE"
