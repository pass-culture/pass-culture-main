"""change_cancellation_date_psql_function

Revision ID: f65cb6d7ef9b
Revises: 7fcfdc9beb40
Create Date: 2021-08-16 17:37:45.903520

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "f65cb6d7ef9b"
down_revision = "7fcfdc9beb40"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    CREATE OR REPLACE FUNCTION public.save_cancellation_date() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
                BEGIN
                    IF NEW."isCancelled" IS TRUE AND OLD."cancellationDate" IS NULL AND NEW."cancellationDate" IS NULL THEN
                        NEW."cancellationDate" = NOW();
                    ELSIF NEW."isCancelled" IS FALSE AND OLD."isCancelled" IS TRUE AND NEW."cancellationDate" IS NOT NULL THEN
                        NEW."cancellationDate" = null;
                    END IF;
                    RETURN NEW;
                END;
            $$;
        """
    )


def downgrade() -> None:
    """
    CREATE OR REPLACE FUNCTION public.save_cancellation_date() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
                BEGIN
                    IF NEW."isCancelled" IS TRUE AND OLD."cancellationDate" IS NULL THEN
                        NEW."cancellationDate" = NOW();
                    ELSIF NEW."isCancelled" IS FALSE THEN
                        NEW."cancellationDate" = null;
                    END IF;
                    RETURN NEW;
                END;
            $$;
    """
