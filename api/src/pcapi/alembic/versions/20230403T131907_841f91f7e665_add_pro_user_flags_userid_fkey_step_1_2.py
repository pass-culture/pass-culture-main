"""Add user_pro_flags_userId_fkey (step 1/2)"""
from alembic import op

from pcapi import settings


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "841f91f7e665"
down_revision = "adeb447a5a8a"
branch_labels = None
depends_on = None


FOREIGN_KEY_NAME = "user_pro_flags_userId_fkey"


def upgrade() -> None:
    op.execute("""SET SESSION statement_timeout='300s'""")
    op.execute(
        f"""
        ALTER TABLE user_pro_flags DROP CONSTRAINT IF EXISTS "{FOREIGN_KEY_NAME}";
        ALTER TABLE user_pro_flags 
        ADD CONSTRAINT "{FOREIGN_KEY_NAME}" FOREIGN KEY ("userId") REFERENCES "user" ("id") ON DELETE CASCADE NOT VALID;
        """
    )
    op.execute(f"""SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}""")


def downgrade() -> None:
    op.execute(
        f"""
        ALTER TABLE user_pro_flags 
        DROP CONSTRAINT IF EXISTS "{FOREIGN_KEY_NAME}";
        """
    )
