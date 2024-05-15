"""add venue.offererAddressId FK constraint"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fdb469eddd52"
down_revision = "ad995e8eff73"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_foreign_key(
        "venue_offererAddressId", "venue", "offerer_address", ["offererAddressId"], ["id"], postgresql_not_valid=True
    )


def downgrade() -> None:
    op.drop_constraint("venue_offererAddressId", "venue", type_="foreignkey")
