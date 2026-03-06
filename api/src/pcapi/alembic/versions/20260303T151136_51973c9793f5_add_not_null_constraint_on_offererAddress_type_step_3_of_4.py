"""Add NOT NULL constraint on "offererAddress.type" (step 3 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "51973c9793f5"
down_revision = "1d26ab58b9c0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.alter_column("offerer_address", "type", nullable=False)
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.alter_column("offerer_address", "venueId", nullable=False)


def downgrade() -> None:
    op.alter_column("offerer_address", "type", nullable=True)
    op.alter_column("offerer_address", "venueId", nullable=True)
