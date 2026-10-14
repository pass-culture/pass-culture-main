"""Validate cultural favorite targets after deployment."""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
revision = "81c6d0f3a4b2"
down_revision = "2bd9f0e0fdc1"
branch_labels: tuple[str] | None = None
depends_on = "7e4a2b9c610d"


def upgrade() -> None:
    for name in (
        "favorite_work_id_fkey",
        "favorite_artist_id_fkey",
        "favorite_offer_origin_id_fkey",
        "favorite_exactly_one_target",
        "favorite_origin_requires_work",
        "favorite_date_created_not_null",
    ):
        op.execute(f'ALTER TABLE favorite VALIDATE CONSTRAINT "{name}"')
    op.alter_column("favorite", "dateCreated", existing_type=sa.DateTime(), nullable=False)
    op.drop_constraint("favorite_date_created_not_null", "favorite", type_="check")
    op.drop_constraint("unique_favorite", "favorite", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("unique_favorite", "favorite", ["userId", "offerId"])
    op.alter_column("favorite", "dateCreated", existing_type=sa.DateTime(), nullable=True)
    op.create_check_constraint(
        "favorite_date_created_not_null", "favorite", '"dateCreated" IS NOT NULL', postgresql_not_valid=True
    )
