"""remove_pro_tuto_feature_flipping

Revision ID: fccbd701588b
Revises: 6cc6a0de4be6
Create Date: 2021-03-10 15:31:07.173866

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "fccbd701588b"
down_revision = "6cc6a0de4be6"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DELETE FROM feature WHERE name = 'PRO_TUTO'")


def downgrade():
    op.execute(
        "INSERT INTO feature (name, description, \"isActive\") VALUES ('PRO_TUTO', 'Permettre l affichage des cartes tuto du portail pro', False)"
    )
