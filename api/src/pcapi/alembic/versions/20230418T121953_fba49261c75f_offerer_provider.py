"""offerer_provider : add offerer_provider constraints (step 4 of 6)
"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "fba49261c75f"
down_revision = "f67ecae084d5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE offerer_provider ADD CONSTRAINT "offerer_provider_offererId_fkey" FOREIGN KEY ("offererId") REFERENCES "offerer" ("id") ON DELETE CASCADE NOT VALID
        """
    )
    op.execute(
        """
        ALTER TABLE offerer_provider ADD CONSTRAINT "offerer_provider_providerId_fkey" FOREIGN KEY ("providerId") REFERENCES "provider" ("id") NOT VALID
        """
    )
    op.execute(
        """
        ALTER TABLE offerer_provider ADD CONSTRAINT "unique_offerer_provider" UNIQUE ("offererId", "providerId");
        """
    )
    op.execute(
        """
        ALTER TABLE provider DROP CONSTRAINT IF EXISTS "check_provider_has_localclass_or_apiUrl";
        """
    )


def downgrade() -> None:
    pass
