"""add primary key to role_backoffice_profile
"""
from alembic import op


revision = "9f7d2f05b501"
down_revision = "3ad10501291a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Replace unique constraint by a composite primary key
    """

    op.execute(
        """
        BEGIN;

        ALTER TABLE
            role_backoffice_profile
        DROP CONSTRAINT IF EXISTS
            "role_backoffice_profile_roleId_profileId_key";

        ALTER TABLE
            role_backoffice_profile
        ADD CONSTRAINT
            "role_backoffice_profile_pkey"
            PRIMARY KEY ("roleId", "profileId");

        COMMIT;
        """
    )


def downgrade() -> None:
    """
    Remove composite primary key and set back the unique constraint
    """
    op.execute(
        """
        BEGIN;

        ALTER TABLE
            role_backoffice_profile
        DROP CONSTRAINT IF EXISTS
            "role_backoffice_profile_pkey";

        ALTER TABLE
            role_backoffice_profile
        ADD CONSTRAINT
            "role_backoffice_profile_roleId_profileId_key"
            UNIQUE("roleId", "profileId");

        COMMIT;
        """
    )
