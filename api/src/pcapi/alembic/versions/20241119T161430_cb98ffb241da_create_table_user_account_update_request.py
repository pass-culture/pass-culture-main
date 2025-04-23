"""Create table UserAccountUpdateRequest"""

from alembic import op
import sqlalchemy as sa

from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.utils.db import MagicEnum


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "cb98ffb241da"
down_revision = "025aaed1c957"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_account_update_request",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dsApplicationId", sa.BigInteger(), nullable=False),
        sa.Column("status", MagicEnum(GraphQLApplicationStates), nullable=False),
        sa.Column("dateCreated", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("dateLastStatusUpdate", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("firstName", sa.Text(), nullable=True),
        sa.Column("lastName", sa.Text(), nullable=True),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("birthDate", sa.Date(), nullable=True),
        sa.Column("userId", sa.BigInteger(), nullable=True),
        sa.Column("newEmail", sa.Text(), nullable=True),
        sa.Column("newPhoneNumber", sa.Text(), nullable=True),
        sa.Column("newFirstName", sa.Text(), nullable=True),
        sa.Column("newLastName", sa.Text(), nullable=True),
        sa.Column("allConditionsChecked", sa.Boolean(), nullable=False),
        sa.Column("lastInstructorId", sa.BigInteger(), nullable=True),
        sa.Column("dateLastUserMessage", sa.DateTime(), nullable=True),
        sa.Column("dateLastInstructorMessage", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["lastInstructorId"],
            ["user.id"],
            postgresql_not_valid=True,
        ),
        sa.ForeignKeyConstraint(
            ["userId"],
            ["user.id"],
            postgresql_not_valid=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_account_update_request_dsApplicationId"),
        "user_account_update_request",
        ["dsApplicationId"],
        unique=True,
    )
    op.create_index(
        op.f("ix_user_account_update_request_userId"),
        "user_account_update_request",
        ["userId"],
    )
    op.create_index(
        op.f("ix_user_account_update_request_lastInstructorId"),
        "user_account_update_request",
        ["lastInstructorId"],
    )


def downgrade() -> None:
    op.drop_table("user_account_update_request")
