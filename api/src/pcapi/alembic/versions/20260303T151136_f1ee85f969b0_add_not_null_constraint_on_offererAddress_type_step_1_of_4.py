"""Add NOT NULL constraint on "offererAddress.type" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f1ee85f969b0"
down_revision = "cb2f79ae8fc2"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE offerer_address DROP CONSTRAINT IF EXISTS "offererAddress_type_not_null_constraint";
        ALTER TABLE offerer_address ADD CONSTRAINT "offererAddress_type_not_null_constraint" CHECK ("type" IS NOT NULL) NOT VALID;
        ALTER TABLE offerer_address DROP CONSTRAINT IF EXISTS "offererAddress_venueId_not_null_constraint";
        ALTER TABLE offerer_address ADD CONSTRAINT "offererAddress_venueId_not_null_constraint" CHECK ("venueId" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("offererAddress_type_not_null_constraint", table_name="offerer_address")
    op.drop_constraint("offererAddress_venueId_not_null_constraint", table_name="offerer_address")
