"""Add NOT NULL constraint on "offerer.siren" (step 4 of 4)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "f9d85badd67d"
down_revision = "57751e8826f0"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("offerer_siren_not_null_constraint", table_name="offerer")


def downgrade() -> None:
    op.execute(
        """ALTER TABLE "offerer" ADD CONSTRAINT "offerer_siren_not_null_constraint" CHECK ("siren" IS NOT NULL) NOT VALID"""
    )
