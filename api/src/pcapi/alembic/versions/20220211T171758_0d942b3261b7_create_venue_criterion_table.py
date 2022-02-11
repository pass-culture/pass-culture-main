"""create venue criterion table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0d942b3261b7"
down_revision = "5507ba019ce1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "venue_criterion",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("criterionId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["criterionId"],
            ["criterion.id"],
        ),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_venue_criterion_criterionId"), "venue_criterion", ["criterionId"], unique=False)
    op.create_index(op.f("ix_venue_criterion_venueId"), "venue_criterion", ["venueId"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_venue_criterion_venueId"), table_name="venue_criterion")
    op.drop_index(op.f("ix_venue_criterion_criterionId"), table_name="venue_criterion")
    op.drop_table("venue_criterion")
