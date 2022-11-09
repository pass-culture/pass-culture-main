"""add primary key to role_permission
"""
from alembic import op

from pcapi import settings


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "8b0574f4aa1b"
down_revision = "ffd6d7217351"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("COMMIT")
    op.execute("""SET SESSION statement_timeout = '900s'""")

    # fill ids
    op.execute(
        """
        BEGIN ;

        -- add nullable id column
        ALTER TABLE role_permission
        ADD COLUMN IF NOT EXISTS "id" bigint NULL ;

        -- fill null ids with sequence
        CREATE SEQUENCE IF NOT EXISTS role_permission_seq ;

        UPDATE role_permission
        SET "id" = nextval('role_permission_seq') ;

        -- transform id into primary key
        ALTER TABLE role_permission
        ALTER "id" SET NOT NULL ;

        ALTER TABLE role_permission
        ALTER "id" SET DEFAULT nextval('role_permission_seq'::regclass) ;

        ALTER TABLE role_permission
        ADD PRIMARY KEY ("id") ;

        COMMIT ;
        """
    )

    op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")


def downgrade():
    op.drop_column("role_permission", "id")
