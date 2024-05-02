"""create users for the tools"""

import secrets

from alembic import op

from pcapi import settings
from pcapi.utils import secrets as secrets_utils


# pre/post deployment: post
# revision identifiers, used by Alembic.
revision = "ca19ecfe0c74"
down_revision = "34a1a2acff4f"
branch_labels: tuple[str] | None = None
depends_on: list[str] | None = None


def upgrade() -> None:
    db_name = settings.DATABASE_URL.split("/")[-1]  # type: ignore [union-attr]
    env = settings.ENV
    # create and configure user for backend
    op.execute(
        f"CREATE USER backend WITH LOGIN NOINHERIT PASSWORD '{secrets_utils.get(f'password_postgresql_{env}_backend', secrets.token_hex(20))}';"
    )
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO backend;")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO backend;")

    # create and configure user for backoffice
    op.execute(
        f"CREATE USER backoffice WITH LOGIN NOINHERIT PASSWORD '{secrets_utils.get(f'password_postgresql_{env}_backoffice', secrets.token_hex(20))}';"
    )
    op.execute(
        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO backoffice;"
    )
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO backoffice;")

    # create and configure user for cron jobs
    op.execute(
        f"CREATE USER cron WITH LOGIN NOINHERIT PASSWORD '{secrets_utils.get(f'password_postgresql_{env}_cron', secrets.token_hex(20))}';"
    )
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO cron;")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cron;")

    # create and configure user for console jobs
    op.execute(
        f"CREATE USER console WITH LOGIN NOINHERIT PASSWORD '{secrets_utils.get(f'password_postgresql_{env}_console', secrets.token_hex(20))}';"
    )
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO console;")
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO console;")

    # create and configure user with read_only rights for supervision
    op.execute(
        f"CREATE USER passculture_readonly WITH LOGIN NOINHERIT PASSWORD '{secrets_utils.get(f'password_postgresql_{env}_passculture_readonly', secrets.token_hex(20))}';"
    )
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO passculture_readonly;")
    op.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO passculture_readonly;")

    # configure auditor
    op.execute("CREATE ROLE auditor WITH NOLOGIN;")
    op.execute(f"""ALTER DATABASE "{db_name}" SET pgaudit.role = 'auditor';""")
    op.execute('GRANT INSERT, UPDATE, DELETE ON "bank_information" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "cashflow" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "cashflow_pricing" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "deposit" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "finance_event" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "invoice" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "invoice_cashflow" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "payment" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "payment_message" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "payment_status" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "pricing" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "venue_reimbursement_point_link" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "bank_account" TO auditor;')
    op.execute('GRANT INSERT, UPDATE, DELETE ON "venue_bank_account_link" TO auditor;')


def downgrade() -> None:
    db_name = settings.DATABASE_URL.split("/")[-1]  # type: ignore [union-attr]

    op.execute(f"""ALTER DATABASE "{db_name}" SET pgaudit.role = '';""")
    op.execute("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM auditor")
    op.execute("DROP ROLE IF EXISTS auditor")

    op.execute("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM backend")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL PRIVILEGES ON TABLES FROM backend;")
    op.execute("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM backoffice")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL PRIVILEGES ON TABLES FROM backoffice;")
    op.execute("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM cron")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL PRIVILEGES ON TABLES FROM cron;")
    op.execute("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM console")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL PRIVILEGES ON TABLES FROM console;")
    op.execute("REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM passculture_readonly")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL PRIVILEGES ON TABLES FROM passculture_readonly;")
    op.execute("DROP USER IF EXISTS backend, backoffice, cron, console, passculture_readonly")
