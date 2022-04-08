"""alter_has_seen_pro_rgs_to_not_null
"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "11f137937ae5"
down_revision = "6ee927d299b1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        SET SESSION statement_timeout = '400s'
        """
    )
    with op.get_context().autocommit_block():
        op.execute(
            """
        DO $$
        DECLARE
            min_id bigint; max_id bigint;
            batch_size int := 100000;
        BEGIN
            SELECT Max(id),min(id) INTO max_id, min_id FROM "user";
            -- This condition is for CirecleCi or empty database initialisation
            IF max_id is Null THEN max_id:=1; min_id:=1;
            END IF;
            FOR j IN min_id..max_id BY batch_size LOOP
                UPDATE "user" SET "hasSeenProRgs" = False
                WHERE id >= j AND id < j+batch_size AND "hasSeenProRgs" is Null;
                COMMIT;
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
        """
        )
    op.alter_column(
        "user", "hasSeenProRgs", existing_type=sa.BOOLEAN(), server_default=sa.text("false"), nullable=False
    )
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade():
    op.alter_column("user", "hasSeenProRgs", existing_type=sa.BOOLEAN(), server_default=None, nullable=True)
