"""reset adage venue address FK constraint: add on delete cascade"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "f54ee3618926"
down_revision = "9a4a8ab82816"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        """
        alter table
            adage_venue_address
        drop
            constraint "adage_venue_address_venueId_fkey" ,
        add
            foreign key("venueId") references venue(id) on delete CASCADE;
    """
    )


def downgrade() -> None:
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.execute(
        """
        alter table
            adage_venue_address
        drop
            constraint "adage_venue_address_venueId_fkey" ,
        add
            foreign key("venueId") references venue(id);
    """
    )
