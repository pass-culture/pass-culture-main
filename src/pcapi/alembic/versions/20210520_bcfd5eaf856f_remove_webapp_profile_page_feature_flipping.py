"""remove_WEBAPP_PROFILE_PAGE_feature_flipping

Revision ID: ae87394773a0
Revises: e63d336e9da8
Create Date: 2021-05-20 15:31:07.173866

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ae87394773a0"
down_revision = "e63d336e9da8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM feature WHERE name = 'WEBAPP_PROFILE_PAGE'")


def downgrade():
    op.execute(
        "INSERT INTO feature (name, description, \"isActive\") VALUES ('WEBAPP_PROFILE_PAGE', 'Permettre l affichage de la page profil (route dédiée + navbar)', True)"
    )
