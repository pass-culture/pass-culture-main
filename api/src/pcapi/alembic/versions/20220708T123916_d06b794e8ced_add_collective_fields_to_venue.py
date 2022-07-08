"""add_collective_fields_to_venue
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# pre/post deployment: pre
# revision identifiers, used by Alembic.
revision = "d06b794e8ced"
down_revision = "d0ab8c9d794e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "educational_domain_venue",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("educationalDomainId", sa.BigInteger(), nullable=False),
        sa.Column("venueId", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["educationalDomainId"], ["educational_domain.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["venueId"], ["venue.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("educationalDomainId", "venueId", name="unique_educational_domain_venue"),
    )
    op.create_index(
        op.f("ix_educational_domain_venue_educationalDomainId"),
        "educational_domain_venue",
        ["educationalDomainId"],
        unique=False,
    )
    op.add_column("venue", sa.Column("collectiveDescription", sa.Text(), nullable=True))
    op.add_column(
        "venue",
        sa.Column(
            "collectiveStudents",
            postgresql.ARRAY(
                sa.Enum(
                    "COLLEGE4", "COLLEGE3", "CAP1", "CAP2", "GENERAL2", "GENERAL1", "GENERAL0", name="studentlevels"
                )
            ),
            server_default="{}",
            nullable=True,
        ),
    )
    op.add_column("venue", sa.Column("collectiveWebsite", sa.Text(), nullable=True))
    op.add_column(
        "venue", sa.Column("collectiveInterventionArea", postgresql.JSONB(astext_type=sa.Text()), nullable=True)  # type: ignore [call-arg]
    )
    op.add_column("venue", sa.Column("collectiveNetwork", postgresql.JSONB(astext_type=sa.Text()), nullable=True))  # type: ignore [call-arg]
    op.add_column("venue", sa.Column("collectiveAccessInformation", sa.Text(), nullable=True))
    op.add_column("venue", sa.Column("collectivePhone", sa.Text(), nullable=True))
    op.add_column("venue", sa.Column("collectiveEmail", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("venue", "collectiveEmail")
    op.drop_column("venue", "collectivePhone")
    op.drop_column("venue", "collectiveAccessInformation")
    op.drop_column("venue", "collectiveNetwork")
    op.drop_column("venue", "collectiveInterventionArea")
    op.drop_column("venue", "collectiveWebsite")
    op.drop_column("venue", "collectiveStudents")
    op.drop_column("venue", "collectiveDescription")
    op.drop_index(op.f("ix_educational_domain_venue_educationalDomainId"), table_name="educational_domain_venue")
    op.drop_table("educational_domain_venue")
