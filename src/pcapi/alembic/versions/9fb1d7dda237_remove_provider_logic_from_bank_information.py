"""remove_provider_logic_from_bank_information

Revision ID: 9fb1d7dda237
Revises: 1cc3d2f75586
Create Date: 2020-05-26 16:12:04.930061

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.schema import ForeignKey


# revision identifiers, used by Alembic.
revision = "9fb1d7dda237"
down_revision = "1cc3d2f75586"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("check_providable_with_provider_has_idatproviders", "bank_information")
    op.drop_column("bank_information", "idAtProviders")
    op.drop_column("bank_information", "fieldsUpdated")
    op.drop_column("bank_information", "lastProviderId")
    op.alter_column("bank_information", "dateModifiedAtLastProvider", new_column_name="dateModified")


def downgrade():
    op.add_column("bank_information", sa.Column("idAtProviders", sa.String(70), unique=True))
    op.add_column(
        "bank_information", sa.Column("fieldsUpdated", sa.ARRAY(sa.String(100)), nullable=False, server_default="{}")
    )
    op.add_column(
        "bank_information", sa.Column("lastProviderId", sa.BigInteger, ForeignKey("provider.id"), nullable=True)
    )
    op.create_check_constraint(
        constraint_name="check_providable_with_provider_has_idatproviders",
        table_name="bank_information",
        condition='"lastProviderId" IS NULL OR "idAtProviders" IS NOT NULL',
    )
    op.alter_column("bank_information", "dateModified", new_column_name="dateModifiedAtLastProvider")
