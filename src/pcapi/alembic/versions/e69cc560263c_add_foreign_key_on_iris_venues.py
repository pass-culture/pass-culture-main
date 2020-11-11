"""add_foreign_key_on_iris_venues

Revision ID: e69cc560263c
Revises: ba456c84727a
Create Date: 2020-03-06 15:07:04.278000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e69cc560263c"
down_revision = "ba456c84727a"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("iris_venues", "venueId", nullable=False)
    op.alter_column("iris_venues", "irisId", nullable=False)

    op.create_foreign_key(
        "iris_venues_irisId_fkey",
        "iris_venues",
        "iris_france",
        ["irisId"],
        ["id"],
    )
    op.create_foreign_key(
        "iris_venues_venueId_fkey",
        "iris_venues",
        "venue",
        ["venueId"],
        ["id"],
    )


def downgrade():
    op.alter_column("iris_venues", "venueId", nullable=True)
    op.alter_column("iris_venues", "irisId", nullable=True)
    op.drop_constraint("iris_venues_irisId_fkey", "iris_venues", type_="foreignkey")
    op.drop_constraint("iris_venues_venueId_fkey", "iris_venues", type_="foreignkey")
