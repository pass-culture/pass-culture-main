"""Generate Alembic migrations that safely add a NOT NULL constraint
on a column of a large table and/or a table that is frequently
modified.

Usage:

    $ python bin/alembic_add_not_null_constraint --table TABLE --column COLUMN

Adding such a constraint on a large table should not be done in one
step: this would require PostgreSQL to scan the whole table, lock it
and thus block updates on that table. Instead, we first create the
constraint with "NOT VALID" and then validate it. For further details
about what is done, see comments in the code below.

Reference: https://www.postgresql.org/docs/current/sql-altertable.html#SQL-ALTERTABLE-NOTES
"""

import argparse
import configparser
import datetime
import pathlib
import string
import subprocess
import sys

import alembic.util as alembic_util

import pcapi


ROOT_DIR = pathlib.Path(pcapi.__path__[0])
ALEMBIC_INI_FILE = ROOT_DIR.parent.parent / "alembic.ini"
ALEMBIC_DIR = ROOT_DIR / "alembic"
ALEMBIC_TEMPLATE = ALEMBIC_DIR / "script.py.mako"
ALEMBIC_VERSION_DIR = ALEMBIC_DIR / "versions"


def _get_alembic_version_filename_template():
    parser = configparser.ConfigParser()
    with open(ALEMBIC_INI_FILE) as fp:
        parser.read_file(fp)
    return parser["alembic"]["file_template"]


ALEMBIC_VERSION_FILENAME_TEMPLATE = _get_alembic_version_filename_template()


# Add a first constraint with NOT VALID. It's fast, does not require a
# scan and does not lock the whole table. Note that this is "CHECK
# CONSTRAINT" on the table.
STEP_1 = {
    "upgrade": """
    op.execute(
        '''
        ALTER TABLE "$table" DROP CONSTRAINT IF EXISTS "$constraint";
        ALTER TABLE "$table" ADD CONSTRAINT "$constraint" CHECK ("$column" IS NOT NULL) NOT VALID;
        '''
    )
    """,
    "downgrade": """
    op.drop_constraint("$constraint", table_name="$table")
    """,
}


# Validate the constraint. It scans the whole table (which takes time,
# hence the higher statement timeout) but requires only a "SHARE
# UPDATE EXCLUSIVE" lock on the table (which allows UPDATE statements
# on the table).
STEP_2 = {
    "imports": """
from pcapi import settings
    """,
    "upgrade": """
    with op.get_context().autocommit_block():
        op.execute("SET SESSION statement_timeout = '300s'")
        op.execute('ALTER TABLE "$table" VALIDATE CONSTRAINT "$constraint"')
        op.execute(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}")
    """,
    "downgrade": """
    pass
    """,
}


# Make the column NOT NULL. This is not stricly necessary, but such a
# constraint is linked to the column (and not the table) and clearly
# appears when running "\d <table>", contrary to our "CHECK
# CONSTRAINT" created in the first step. This is fast because
# PostgreSQL detects that our "CHECK CONSTRAINT" is similar.
STEP_3 = {
    "upgrade": """
    op.alter_column("$table", "$column", nullable=False)
    """,
    "downgrade": """
    op.alter_column("$table", "$column", nullable=True)
    """,
}


# Drop our first constraint.
STEP_4 = {
    "upgrade": """
    op.drop_constraint("$constraint", table_name="$table")
    """,
    "downgrade": '''
    op.execute("""ALTER TABLE "$table" ADD CONSTRAINT "$constraint" CHECK ("$column" IS NOT NULL) NOT VALID""")
    ''',
}

STEPS = (STEP_1, STEP_2, STEP_3, STEP_4)


def main():
    args = parse_args()

    bindings = {
        "table": args.table,
        "column": args.column,
        "constraint": f"{args.table}_{args.column}_not_null_constraint",
    }

    config = fake_alembic_config_for_template()
    down_revision = get_current_post_head()
    for i_step, step in enumerate(STEPS, 1):
        slug = f"add_not_null_constraint_on_{args.table}_{args.column}_step_{i_step}_of_{len(STEPS)}"
        message = f'Add NOT NULL constraint on "{args.table}.{args.column}" (step {i_step} of {len(STEPS)})'
        upgrade = string.Template(step["upgrade"]).substitute(bindings).strip()
        downgrade = string.Template(step["downgrade"]).substitute(bindings).strip()
        imports = step.get("imports", "").strip()
        rev_id = alembic_util.rev_id()
        dt = datetime.datetime.now()
        path = ALEMBIC_VERSION_DIR / (
            ALEMBIC_VERSION_FILENAME_TEMPLATE
            % {
                "rev": rev_id,
                "slug": slug,
                "year": dt.year,
                "month": dt.month,
                "day": dt.day,
                "hour": dt.hour,
                "minute": dt.minute,
                "second": dt.second,
            }
            + ".py"
        )

        with alembic_util.status(f"Generating {path}"):
            alembic_util.template_to_file(
                str(ALEMBIC_TEMPLATE),
                path,
                "utf-8",
                # The following kwargs are used to populate the template.
                message=message,
                imports=imports,
                config=config,
                up_revision=rev_id,
                down_revision=down_revision,
                branch_labels=None,
                depends_on=None,
                upgrades=upgrade,
                downgrades=downgrade,
            )
        down_revision = rev_id


def get_current_post_head():
    command = "alembic show post@head"
    result = subprocess.run(
        command.split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    encoding = "utf-8"
    if result.stderr or b"FAILED" in result.stdout:
        out = result.stderr.decode(encoding) or result.stdout.decode(encoding).strip()
        sys.exit("\n".join((f"Got error when running `{command}`", out)))
    for line in result.stdout.decode(encoding).split("\n"):
        if line.startswith("Rev:"):  # e.g. `Rev: 329eb64be6c5 (head)`
            return line.split(" ")[1]
    message = "\n".join(
        (
            f'Could not determine "post" head from output of `{command}`.',
            'Is there a line that starts with "Rev: "?',
            "Here is the output of that command:",
            "--- 8-> ---",
            result.stdout.decode(encoding),
            "--- 8-> ---",
        )
    )
    sys.exit(message)


def fake_alembic_config_for_template():
    # The template needs an Alembic config object to populate
    # `${config.cmd_opts.head.split("@")[0]}`. We know we want to
    # replace that by "post".
    class Config:
        class CmdOpts:
            head = "post@..."

        cmd_opts = CmdOpts()

    return Config()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--table", required=True)
    parser.add_argument("--column", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    main()
