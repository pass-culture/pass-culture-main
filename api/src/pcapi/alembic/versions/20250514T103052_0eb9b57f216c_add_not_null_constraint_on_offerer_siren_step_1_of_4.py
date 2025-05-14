"""Add NOT NULL constraint on "offerer.siren" (step 1 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "0eb9b57f216c"
down_revision = "60fdd63d8828"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "offerer" DROP CONSTRAINT IF EXISTS "offerer_siren_not_null_constraint";
        ALTER TABLE "offerer" ADD CONSTRAINT "offerer_siren_not_null_constraint" CHECK ("siren" IS NOT NULL) NOT VALID;
        """
    )


def downgrade() -> None:
    op.drop_constraint("offerer_siren_not_null_constraint", table_name="offerer")
