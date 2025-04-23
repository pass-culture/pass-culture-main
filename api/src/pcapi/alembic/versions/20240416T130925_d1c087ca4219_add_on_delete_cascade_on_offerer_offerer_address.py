"""Add on_delete cascade on offerer offerer_address"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d1c087ca4219"
down_revision = "dc623fa7d47b"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE "offerer_address" DROP CONSTRAINT IF EXISTS "offerer_address_offererId_fkey";
        ALTER TABLE "offerer_address" ADD CONSTRAINT "offerer_address_offererId_fkey" FOREIGN KEY("offererId") REFERENCES offerer (id) on delete CASCADE NOT VALID;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE "offerer_address" DROP CONSTRAINT IF EXISTS "offerer_address_offererId_fkey";
        ALTER TABLE offerer_address ADD CONSTRAINT "offerer_address_offererId_fkey" FOREIGN KEY("offererId") REFERENCES offerer (id) NOT VALID;
        """
    )
