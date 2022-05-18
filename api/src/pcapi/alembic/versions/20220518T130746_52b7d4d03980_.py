"""migrate user.activity values from the old values to the new ones"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "52b7d4d03980"
down_revision = "06190162f083"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Mappings:
    # No changes:
    #     <null>
    #     Alternant
    #     Apprenti
    #     Apprenti, Alternant, Volontaire en service civique rémunéré
    #        -> Cannot be changed since we cannot know which one is the correct one
    #     Chômeur
    #     Collégien
    #     Employé
    #     Étudiant
    #     Inactif
    #     Lycéen
    #     Volontaire
    # Values to update
    #     Chômeur, En recherche d'emploi                                    -> Chômeur
    #     Inactif (ni en emploi ni au chômage), En incapacité de travailler -> Inactif
    #     Etudiant                                                          -> Étudiant
    #     En recherche d'emploi ou chômeur                                  -> Chômeur
    #     <empty string>                                                    -> NULL

    op.execute("""update "user" set activity='Chômeur' where activity='Chômeur, En recherche d''emploi'""")
    op.execute(
        """update "user" set activity='Inactif' where activity='Inactif (ni en emploi ni au chômage), En incapacité de travailler'"""
    )
    op.execute("""update "user" set activity='Étudiant' where activity='Etudiant'""")
    op.execute("""update "user" set activity='Chômeur' where activity='En recherche d''emploi ou chômeur'""")
    op.execute("""update "user" set activity=NULL where activity=''""")


def downgrade() -> None:
    pass
