import pytest

from pcapi.models import UserOfferer
from pcapi.repository import repository
from pcapi.scripts.user_offerer.delete_user_offerer_from_csv import (
    _delete_user_offerers_from_rows,
)
from pcapi.model_creators.generic_creators import (
    create_user,
    create_user_offerer,
    create_offerer,
)


class DeleteUserOfferersFromFileTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_delete_user_offerers_in_csv(self):
        # Given
        user1 = create_user(idx="20", email="1@toto.fr")
        user2 = create_user(idx="21", email="2@toto.fr")
        user3 = create_user(idx="22", email="3@toto.fr")
        offerer1 = create_offerer(idx="15", siren="1")
        offerer2 = create_offerer(idx="16", siren="2")
        offerer3 = create_offerer(idx="17", siren="3")
        user_offerer1 = create_user_offerer(user1, offerer1)
        user_offerer2 = create_user_offerer(user2, offerer2)
        user_offerer3 = create_user_offerer(user3, offerer3)

        repository.save(user_offerer1, user_offerer2, user_offerer3)

        self.csv_rows = [
            [
                "Lien structure sur le portail PRO",
                "ID Structure",
                "Email utilisateur",
                "ID Utilisateur",
                "Commentaire",
            ],
            ["unused", "15", "unused", "20", "unused", "unused", "unused", "unused"],
            ["unused", "16", "unused", "21", "unused", "unused", "unused", "unused"],
        ]

        # When
        _delete_user_offerers_from_rows(self.csv_rows)
        user_offerers = UserOfferer.query.all()

        # Then
        assert len(user_offerers) == 1
        assert user_offerers[0].userId == user3.id
        assert user_offerers[0].offererId == offerer3.id
