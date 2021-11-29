import pytest

import pcapi.core.offers.factories as offers_factories
from pcapi.models.user_offerer import UserOfferer
from pcapi.scripts.user_offerer.delete_user_offerer_from_csv import _delete_user_offerers_from_rows


@pytest.mark.usefixtures("db_session")
def test_should_delete_user_offerers_in_csv():
    # Given
    user_offerer1 = offers_factories.UserOffererFactory()
    user_offerer2 = offers_factories.UserOffererFactory()
    user_offerer3 = offers_factories.UserOffererFactory()

    csv_rows = [
        [
            "Lien structure sur le portail PRO",
            "ID Structure",
            "Email utilisateur",
            "ID Utilisateur",
            "Commentaire",
        ],
        ["unused", user_offerer1.offererId, "unused", user_offerer1.userId, "unused", "unused", "unused", "unused"],
        ["unused", user_offerer2.offererId, "unused", user_offerer2.userId, "unused", "unused", "unused", "unused"],
    ]

    # When
    _delete_user_offerers_from_rows(csv_rows)

    # Then
    user_offerer = UserOfferer.query.one()
    assert user_offerer == user_offerer3
