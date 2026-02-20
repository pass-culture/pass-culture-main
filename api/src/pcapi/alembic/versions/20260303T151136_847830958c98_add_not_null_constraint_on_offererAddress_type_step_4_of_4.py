"""Add NOT NULL constraint on "offererAddress.type" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "847830958c98"
down_revision = "51973c9793f5"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("offererAddress_type_not_null_constraint", table_name="offerer_address")
    op.drop_constraint("offererAddress_venueId_not_null_constraint", table_name="offerer_address")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE offerer_address ADD CONSTRAINT "offererAddress_type_not_null_constraint" CHECK ("type" IS NOT NULL) NOT VALID"""
    )
    op.execute(
        """ALTER TABLE offerer_address ADD CONSTRAINT "offererAddress_venueId_not_null_constraint" CHECK ("venueId" IS NOT NULL) NOT VALID"""
    )
