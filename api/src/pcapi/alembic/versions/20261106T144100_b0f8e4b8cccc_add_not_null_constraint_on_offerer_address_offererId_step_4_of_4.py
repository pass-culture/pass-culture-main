"""Add NOT NULL constraint on "offerer_address.offererId" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = 'b0f8e4b8cccc'
down_revision = 'f8e5e2ad69d4'
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("offerer_address_offererId_not_null_constraint", table_name="offerer_address")


def downgrade() -> None:
    op.execute("""ALTER TABLE "offerer_address" ADD CONSTRAINT "offerer_address_offererId_not_null_constraint" CHECK ("offererId" IS NOT NULL) NOT VALID""")
