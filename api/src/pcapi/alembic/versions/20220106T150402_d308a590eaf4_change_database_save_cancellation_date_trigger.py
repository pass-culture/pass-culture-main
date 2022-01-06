"""20220106T150402_d308a590eaf4_change_database_save_cancellation_date_trigger
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "d308a590eaf4"
down_revision = "f6efe8c78450"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
  CREATE OR REPLACE FUNCTION save_cancellation_date()
  RETURNS TRIGGER AS $$
  BEGIN
      IF NEW.status = 'CANCELLED' AND OLD."cancellationDate" IS NULL AND NEW."cancellationDate" IS NULL THEN
          NEW."cancellationDate" = NOW();
      ELSIF NEW.status != 'CANCELLED' THEN
          NEW."cancellationDate" = NULL;
      END IF;
      RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;

  DROP TRIGGER IF EXISTS stock_update_cancellation_date ON booking;

  -- XXX: update anonymize SQL script if you change anything below
  CREATE TRIGGER stock_update_cancellation_date
  BEFORE INSERT OR UPDATE OF status ON booking
  FOR EACH ROW
  EXECUTE PROCEDURE save_cancellation_date()
  """
    )


def downgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION save_cancellation_date()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW."isCancelled" IS TRUE AND OLD."cancellationDate" IS NULL THEN
            NEW."cancellationDate" = NOW();
        ELSIF NEW."isCancelled" IS FALSE THEN
            NEW."cancellationDate" = NULL;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS stock_update_cancellation_date ON booking;

    -- XXX: update anonymize SQL script if you change anything below
    CREATE TRIGGER stock_update_cancellation_date
    BEFORE INSERT OR UPDATE ON booking
    FOR EACH ROW
    EXECUTE PROCEDURE save_cancellation_date()
    """
    )
