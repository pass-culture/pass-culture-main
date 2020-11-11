"""update_booking_to_trigger_checkbooking_only_on_quantity_and_amount

Revision ID: 5c0507247814
Revises: 2b6541bb0076
Create Date: 2020-04-10 07:39:11.211577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5c0507247814"
down_revision = "2b6541bb0076"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DROP TRIGGER IF EXISTS booking_update ON booking;
        CREATE CONSTRAINT TRIGGER booking_update 
        AFTER INSERT 
        OR UPDATE OF quantity, amount, "isCancelled", "isUsed", "userId"  
        ON booking
        FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """
    )


def downgrade():
    op.execute(
        """
        DROP TRIGGER IF EXISTS booking_update ON booking;
        CREATE CONSTRAINT TRIGGER booking_update AFTER INSERT OR UPDATE
        ON booking
        FOR EACH ROW EXECUTE PROCEDURE check_booking()
    """
    )
