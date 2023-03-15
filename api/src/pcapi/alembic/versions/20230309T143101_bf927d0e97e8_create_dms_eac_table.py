"""create_dms_eac_table
"""
from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "bf927d0e97e8"
down_revision = "a8e0474a749c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collective_dms_application",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.Column("state", sa.String(length=30), nullable=False),
        sa.Column("procedure", sa.BigInteger(), nullable=False),
        sa.Column("application", sa.BigInteger(), nullable=False),
        sa.Column("siret", sa.String(length=14), nullable=False),
        sa.Column("lastChangeDate", sa.DateTime(), nullable=False),
        sa.Column("depositDate", sa.DateTime(), nullable=False),
        sa.Column("expirationDate", sa.DateTime(), nullable=False),
        sa.Column("buildDate", sa.DateTime(), nullable=True),
        sa.Column("instructionDate", sa.DateTime(), nullable=True),
        sa.Column("processingDate", sa.DateTime(), nullable=True),
        sa.Column("userDeletionDate", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["venueId"],
            ["venue.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_collective_dms_application_application"), "collective_dms_application", ["application"], unique=False
    )
    op.create_index(
        op.f("ix_collective_dms_application_venueId"), "collective_dms_application", ["venueId"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_collective_dms_application_venueId"), table_name="collective_dms_application")
    op.drop_index(op.f("ix_collective_dms_application_application"), table_name="collective_dms_application")
    op.drop_table("collective_dms_application")
