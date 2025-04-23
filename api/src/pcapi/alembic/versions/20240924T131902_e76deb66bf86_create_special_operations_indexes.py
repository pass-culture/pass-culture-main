"""Create indexes for special events models (new tables)"""

from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "e76deb66bf86"
down_revision = "f171a3dfd689"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            op.f("ix_special_event_eventDate"),
            "special_event",
            ["eventDate"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_special_event_externalId"),
            "special_event",
            ["externalId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_special_event_question_eventId"),
            "special_event_question",
            ["eventId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_special_event_question_externalId"),
            "special_event_question",
            ["externalId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_special_event_response_eventId"),
            "special_event_response",
            ["eventId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_special_event_response_externalId"),
            "special_event_response",
            ["externalId"],
            unique=True,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_special_event_response_userId"),
            "special_event_response",
            ["userId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_special_event_answer_questionId"),
            "special_event_answer",
            ["questionId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            op.f("ix_special_event_answer_responseId"),
            "special_event_answer",
            ["responseId"],
            unique=False,
            postgresql_concurrently=True,
            if_not_exists=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            op.f("ix_special_event_answer_responseId"),
            table_name="special_event_answer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_special_event_answer_questionId"),
            table_name="special_event_answer",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_special_event_response_userId"),
            table_name="special_event_response",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_special_event_response_externalId"),
            table_name="special_event_response",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_special_event_response_eventId"),
            table_name="special_event_response",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_special_event_question_externalId"),
            table_name="special_event_question",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_special_event_question_eventId"),
            table_name="special_event_question",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_special_event_externalId"),
            table_name="special_event",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            op.f("ix_special_event_eventDate"), table_name="special_event", postgresql_concurrently=True, if_exists=True
        )
