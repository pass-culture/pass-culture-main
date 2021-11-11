"""create_venue_contact

Revision ID: 2ed5959876f1
Revises: ff887e7b4f89
Create Date: 2021-08-03 18:44:42.111488

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "2ed5959876f1"
down_revision = "f5997ab962be"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "venue_contact",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("email", sa.String(length=256), nullable=True),
        sa.Column("website", sa.String(length=256), nullable=True),
        sa.Column("phone_number", sa.String(length=64), nullable=True),
        sa.Column("social_medias", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_venue_contact_venueId"), "venue_contact", ["venueId"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_venue_contact_venueId"), table_name="venue_contact")
    op.drop_table("venue_contact")
