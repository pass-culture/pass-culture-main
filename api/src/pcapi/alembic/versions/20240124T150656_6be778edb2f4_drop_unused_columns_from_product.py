"""Drop "isNational", "url", "owningOffererId" & "isSynchronizationCompatible" column to "product" table."""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "6be778edb2f4"
down_revision = "9607ada7a6b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """ALTER TABLE product
        DROP COLUMN IF EXISTS "isNational",
        DROP COLUMN IF EXISTS "url",
        DROP COLUMN IF EXISTS "owningOffererId",
        DROP COLUMN IF EXISTS "isSynchronizationCompatible";
    """
    )


def downgrade() -> None:
    op.execute(
        """ALTER TABLE product
        ADD COLUMN IF NOT EXISTS "isSynchronizationCompatible" BOOLEAN DEFAULT true NOT NULL,
        ADD COLUMN IF NOT EXISTS "owningOffererId" INTEGER,
        ADD COLUMN IF NOT EXISTS url VARCHAR(255),
        ADD COLUMN IF NOT EXISTS "isNational" BOOLEAN DEFAULT false NOT NULL,
        DROP CONSTRAINT IF EXISTS product_owning_offerer_id_fkey,
        ADD CONSTRAINT product_owning_offerer_id_fkey FOREIGN KEY("owningOffererId") REFERENCES offerer (id);
    """
    )
