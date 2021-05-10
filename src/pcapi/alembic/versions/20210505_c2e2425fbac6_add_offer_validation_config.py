from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "c2e2425fbac6"
down_revision = "3af77a192c66"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "offer_validation_config",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dateCreated", sa.DateTime(), nullable=False),
        sa.Column("userId", sa.BigInteger(), nullable=True),
        sa.Column("specs", postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(
            ["userId"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("offer_validation_config")
