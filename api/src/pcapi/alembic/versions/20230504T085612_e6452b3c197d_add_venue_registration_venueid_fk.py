"""Add venue_registration venueId FK step 1/2"""
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e6452b3c197d"
down_revision = "ddd2e5df3da7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This will commit instantyly as soon as it gets a SHARE ROW lock on both tables
    op.create_foreign_key(
        constraint_name="venue_registration_venueId_fkey",
        source_table="venue_registration",
        referent_table="venue",
        local_cols=["venueId"],
        remote_cols=["id"],
        postgresql_not_valid=True,
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(constraint_name="venue_registration_venueId_fkey", table_name="venue_registration")
