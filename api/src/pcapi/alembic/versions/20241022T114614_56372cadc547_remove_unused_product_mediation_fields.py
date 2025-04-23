"""Alter table productMediation delete columns fieldsUpdated and idAtProviders"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "56372cadc547"
down_revision = "22e94edcc427"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_constraint("product_mediation_idAtProviders_key", "product_mediation", type_="unique")
    op.drop_column("product_mediation", "fieldsUpdated")
    op.drop_column("product_mediation", "idAtProviders")


def downgrade() -> None:
    # We sould use a text field with a check constraint.
    # But that would be unaligned with our models. Let's hope we sont revert
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column(
        "product_mediation", sa.Column("idAtProviders", sa.VARCHAR(length=70), autoincrement=False, nullable=True)
    )
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.add_column(
        "product_mediation",
        sa.Column(
            "fieldsUpdated",
            postgresql.ARRAY(sa.VARCHAR(length=100)),
            server_default=sa.text("'{}'::character varying[]"),
            autoincrement=False,
            nullable=True,
        ),
    )
    # This table is only filled with crons during the night, there is no problem locking writes during a MEP
    op.execute("select 1 -- squawk:ignore-next-statement")
    op.create_unique_constraint("product_mediation_idAtProviders_key", "product_mediation", ["idAtProviders"])
