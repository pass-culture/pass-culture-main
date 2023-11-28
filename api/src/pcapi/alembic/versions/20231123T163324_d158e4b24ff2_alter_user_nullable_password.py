"""Add NOT NULL contraint and contraint trigger on `user.password`
"""
from alembic import op
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d158e4b24ff2"
down_revision = "197afaebf455"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("user", "password", existing_type=postgresql.BYTEA(), nullable=True)
    op.execute(
        """
        CREATE OR REPLACE FUNCTION ensure_password_or_sso_exists()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.password IS NULL THEN
                IF NOT EXISTS (SELECT 1 FROM single_sign_on WHERE "userId" = NEW.id) THEN
                    RAISE EXCEPTION 'missingLoginMethod' USING HINT = 'User must have either a password or a single sign-on';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS ensure_password_or_sso_exists ON "user";
        CREATE CONSTRAINT TRIGGER ensure_password_or_sso_exists
        AFTER INSERT OR UPDATE OF password ON "user"
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE PROCEDURE ensure_password_or_sso_exists();
        """
    )


def downgrade() -> None:
    op.alter_column("user", "password", existing_type=postgresql.BYTEA(), nullable=False)
    op.execute('drop trigger if exists ensure_password_or_sso_exists on "user"')
    op.execute("drop function if exists ensure_password_or_sso_exists")
