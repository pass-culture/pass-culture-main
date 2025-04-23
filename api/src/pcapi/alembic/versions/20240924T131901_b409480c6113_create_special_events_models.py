"""Create tables for special events"""

from alembic import op
import sqlalchemy as sa


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "b409480c6113"
down_revision = "c3ae9b34287c"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.create_table(
        "special_event",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("dateCreated", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("externalId", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("eventDate", sa.DateTime(), nullable=True),
        sa.Column("offererId", sa.BigInteger(), nullable=True),
        sa.Column("venueId", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["offererId"], ["offerer.id"], ondelete="SET NULL", postgresql_not_valid=True),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="SET NULL", postgresql_not_valid=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "special_event_question",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("eventId", sa.BigInteger(), nullable=True),
        sa.Column("externalId", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["eventId"],
            ["special_event.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "special_event_response",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("eventId", sa.BigInteger(), nullable=True),
        sa.Column("externalId", sa.Text(), nullable=False),
        sa.Column("dateSubmitted", sa.DateTime(), nullable=False),
        sa.Column("phoneNumber", sa.Text(), nullable=True),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("userId", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["eventId"],
            ["special_event.id"],
        ),
        sa.ForeignKeyConstraint(
            ["userId"],
            ["user.id"],
            postgresql_not_valid=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "special_event_answer",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("responseId", sa.BigInteger(), nullable=True),
        sa.Column("externalId", sa.Text(), nullable=False),
        sa.Column("questionId", sa.BigInteger(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["questionId"],
            ["special_event_question.id"],
        ),
        sa.ForeignKeyConstraint(
            ["responseId"],
            ["special_event_response.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("special_event_answer")
    op.drop_table("special_event_response")
    op.drop_table("special_event_question")
    op.drop_table("special_event")
