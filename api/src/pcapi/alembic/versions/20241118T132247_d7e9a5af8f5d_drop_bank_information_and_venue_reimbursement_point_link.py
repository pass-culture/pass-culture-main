"""Drop BankInformation and VenueReimbursementPointLink"""

import sqlalchemy as sa
from alembic import op


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "d7e9a5af8f5d"
down_revision = "ea991dc8fbfc"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    op.drop_column("cashflow", "bankInformationId")
    op.drop_column("cashflow", "reimbursementPointId")

    op.drop_column("invoice", "reimbursementPointId")

    op.execute("DROP TABLE IF EXISTS bank_information;")
    op.execute("DROP TABLE IF EXISTS venue_reimbursement_point_link;")
    op.execute("DROP TYPE IF EXISTS status;")


def downgrade() -> None:
    # we ignore some statements, as we don't aim to use those tables ever again
    op.execute("select 1 -- squawk:ignore-next-statement")  # ignoring a prefer-bigint-over-int recommendation
    op.execute(
        """
        CREATE TYPE public.status AS ENUM (
            'ACCEPTED',
            'REJECTED',
            'DRAFT'
        );"""
    )
    op.execute("select 1 -- squawk:ignore-next-statement")  # ignoring a prefer-text-field recommendation
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bank_information (
            id bigint NOT NULL,
            "offererId" bigint,
            "venueId" bigint,
            iban character varying(27),
            bic character varying(11),
            "applicationId" integer,
            "dateModified" timestamp without time zone,
            status public.status NOT NULL
        );"""
    )
    op.execute("select 1 -- squawk:ignore-next-statement")  # ignoring a prefer-text-field recommendation
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS venue_reimbursement_point_link (
            id bigint NOT NULL,
            "venueId" bigint NOT NULL,
            "reimbursementPointId" bigint NOT NULL,
            timespan tsrange NOT NULL
        );"""
    )

    op.add_column("cashflow", sa.Column("reimbursementPointId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column("cashflow", sa.Column("bankInformationId", sa.BIGINT(), autoincrement=False, nullable=True))
    op.add_column("invoice", sa.Column("reimbursementPointId", sa.BIGINT(), autoincrement=False, nullable=True))

    op.execute("COMMIT")
    op.create_index(
        "ix_invoice_reimbursementPointId",
        "invoice",
        ["reimbursementPointId"],
        unique=False,
        postgresql_concurrently=True,
        if_not_exists=True,
    )
    op.create_index(
        "ix_cashflow_reimbursementPointId",
        "cashflow",
        ["reimbursementPointId"],
        unique=False,
        postgresql_concurrently=True,
        if_not_exists=True,
    )
    op.create_index(
        "ix_cashflow_bankInformationId",
        "cashflow",
        ["bankInformationId"],
        unique=False,
        postgresql_concurrently=True,
        if_not_exists=True,
    )
    op.execute("BEGIN")
