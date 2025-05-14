"""Make Mediation.fieldsUpdated nullable"""

from alembic import op


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "fa3f1609ac73"
down_revision = "e6e6d0535717"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.alter_column("mediation", "fieldsUpdated", nullable=True)


def downgrade() -> None:
    # We wouldn't want to make it non nullable again
    pass
