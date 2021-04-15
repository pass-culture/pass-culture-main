"""remove_pro_homepage_feature_flipping

Revision ID: 2f3af262e528
Revises: 40754eda1d0f
Create Date: 2021-04-15 13:12:53.834781

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2f3af262e528"
down_revision = "40754eda1d0f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DELETE FROM feature WHERE name = 'PRO_HOMEPAGE'")


def downgrade() -> None:
    op.execute(
        "INSERT INTO feature (name, description, \"isActive\") VALUES ('PRO_HOMEPAGE', 'Permettre l affichage de la nouvelle page d accueil du portail pro', True)"
    )
