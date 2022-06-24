"""alter_isdraft_on_offer_set_not_null
"""
from alembic import op
import sqlalchemy as sa

from pcapi import settings


# revision identifiers, used by Alembic.
revision = "bfd208fa705b"
down_revision = "090834b497b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        SET SESSION statement_timeout = '900s'
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
            SELECT Max(id),min(id) INTO max_id, min_id FROM "offer";
            -- This condition is for CirecleCi or empty database initialisation
            IF max_id is Null THEN max_id:=1; min_id:=1;
            END IF;
            FOR j IN min_id..max_id BY batch_size LOOP
                UPDATE "offer" SET "isDraft" = False
                WHERE id >= j AND id < j+batch_size AND "isDraft" is Null;
                COMMIT;
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
        """
        )
    op.alter_column("offer", "isDraft", existing_type=sa.BOOLEAN(), server_default=sa.text("true"), nullable=False)
    op.execute(
        f"""
        SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}
        """
    )


def downgrade() -> None:
    op.alter_column("offer", "isDraft", existing_type=sa.BOOLEAN(), server_default=None, nullable=True)
