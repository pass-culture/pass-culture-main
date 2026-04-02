"""
Detects significant Alembic migration operations.

Parses one or more Alembic migration files, extracts upgrade() operations
(drops, renames, type changes, additions, creations), then cross-references
them against the set of SQL tables actually imported for each deployment
environment (prod, stg). Prints a Slack-formatted alert for any environment
that has noteworthy changes.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.request
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator


# ---------------------------------------------------------------------------
# Constants — URLs, path prefixes, and branch-to-environment mappings
# ---------------------------------------------------------------------------

REPO_TREE_URL = "https://api.github.com/repos/pass-culture/data-gcp/git/trees/"
SQL_PREFIX = "orchestration/dags/dependencies/applicative_database/sql/"
EXCLUDED_SUBFOLDERS = frozenset(["history"])

# Maps a GitHub branch name to its logical deployment environment label
BRANCH_ENV: dict[str, str] = {
    "production": "prod",
    "master": "stg",
}


# ---------------------------------------------------------------------------
# OpKind — canonical set of detectable migration operation types
# ---------------------------------------------------------------------------

class OpKind(str, Enum):
    """Represents a normalised migration operation type used throughout the pipeline.

    Operations are classified into two severity tiers:
    - Important: destructive or structural changes (drops, renames, type alterations)
    - Notable: additive changes that may still warrant attention (new columns, new tables)
    """

    ADD_COLUMN    = "add_column"
    ALTER_TYPE    = "alter_type"
    CREATE_TABLE  = "create_table"
    DROP_COLUMN   = "drop_column"
    DROP_TABLE    = "drop_table"
    RENAME_COLUMN = "rename_column"
    RENAME_TABLE  = "rename_table"

    @property
    def is_important(self) -> bool:
        """Return True if this operation is destructive or structurally breaking."""
        return self in {
            OpKind.ALTER_TYPE,
            OpKind.DROP_COLUMN,
            OpKind.DROP_TABLE,
            OpKind.RENAME_COLUMN,
            OpKind.RENAME_TABLE,
        }

    @property
    def is_notable(self) -> bool:
        """Return True if this operation is additive but still worth reporting."""
        return self in {OpKind.ADD_COLUMN, OpKind.CREATE_TABLE}

    @property
    def always_notify(self) -> bool:
        """Return True if this operation should be reported regardless of the table subset.

        Currently only CREATE_TABLE qualifies, since new tables are always relevant.
        """
        return self is OpKind.CREATE_TABLE


# ---------------------------------------------------------------------------
# Keyword-to-OpKind mapping — raw code tokens that trigger operation detection
# ---------------------------------------------------------------------------

# Maps raw keyword strings (as they appear in migration source code) to their
# canonical OpKind. Both Python API calls and raw SQL variants are covered.
_KEYWORD_MAP: dict[str, OpKind] = {
    # Important — destructive or structurally breaking operations
    "drop_column":     OpKind.DROP_COLUMN,
    "DROP COLUMN":     OpKind.DROP_COLUMN,
    "alter_column":    OpKind.ALTER_TYPE,
    "ALTER COLUMN":    OpKind.ALTER_TYPE,
    "alter_type":      OpKind.ALTER_TYPE,
    "ALTER TYPE":      OpKind.ALTER_TYPE,
    "drop_table":      OpKind.DROP_TABLE,
    "DROP TABLE":      OpKind.DROP_TABLE,
    "rename_table":    OpKind.RENAME_TABLE,
    "RENAME TO":       OpKind.RENAME_TABLE,
    "new_column_name": OpKind.RENAME_COLUMN,
    "RENAME COLUMN":   OpKind.RENAME_COLUMN,
    # Notable — additive operations
    "add_column":      OpKind.ADD_COLUMN,
    "ADD COLUMN":      OpKind.ADD_COLUMN,
    "create_table":    OpKind.CREATE_TABLE,
    "CREATE TABLE":    OpKind.CREATE_TABLE,
}

# Pre-filtered keyword tuples for fast per-level scanning
_IMPORTANT_KEYWORDS = tuple(k for k, v in _KEYWORD_MAP.items() if v.is_important)
_NOTABLE_KEYWORDS   = tuple(k for k, v in _KEYWORD_MAP.items() if v.is_notable)


# ---------------------------------------------------------------------------
# SlackGroup and SlackTeam — representations for Slack notifications
# ---------------------------------------------------------------------------
@dataclass
class SlackGroup:
    slack_id: str
    name: str


class SlackTeam(Enum):
    DS = SlackGroup(slack_id="S08CVKQ4K9S", name="Data Science")
    DE = SlackGroup(slack_id="S08CT44F7J6", name="Data Engineering")
    DA = SlackGroup(slack_id="S0472K8E413", name="Data Analytics")

    @property
    def name(self) -> str:
        return self.value.name

    @property
    def slack_id(self) -> str:
        return self.value.slack_id

    def fmt_slack_mention(self) -> str:
        return f"<!subteam^{self.slack_id}>"


NOTIFICATION_MATRIX = {"important": {SlackTeam.DE, SlackTeam.DA}, "notable": {SlackTeam.DA}}
# ---------------------------------------------------------------------------
# MigrationOp — a single detected operation inside a migration's upgrade() block
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MigrationOp:
    """Represents one detected operation parsed from an Alembic migration file.

    Attributes:
        hash:      Short commit/revision hash extracted from the filename stem.
        kind:      The canonical OpKind for this operation.
        table:     Name of the affected table, or None if it could not be determined.
        column:    Name of the affected column, or None if not applicable.
        rename_to: Target name for rename operations, or None otherwise.
    """

    hash: str
    kind: OpKind
    table: str | None
    column: str | None
    rename_to: str | None

    def format(self) -> str:
        """Return a human-readable one-line summary of this operation."""
        table = self.table or "unknown"
        if self.kind is OpKind.RENAME_COLUMN and self.column and self.rename_to:
            detail = f"{table}: {self.column} → {self.rename_to}"
        elif self.kind is OpKind.RENAME_TABLE and self.rename_to:
            detail = f"{table} → {self.rename_to}"
        elif self.column:
            detail = f"{table}: {self.column}"
        else:
            detail = table
        return f"[{self.hash}] {self.kind.value} ({detail})"

    def matches_subset(self, tables: set[str]) -> bool:
        """Return True if this operation targets a table present in the given set."""
        return self.table in tables

    def should_notify(self, tables: set[str]) -> bool:
        """Return True if this operation warrants a notification for the given table set.

        Notification is triggered either because the operation always notifies
        (e.g. CREATE_TABLE) or because it targets a table in the subset.
        """
        return self.kind.always_notify or self.matches_subset(tables)


# ---------------------------------------------------------------------------
# OperationExtractor — extracts table, column, and rename_to from a code line
# ---------------------------------------------------------------------------

class OperationExtractor:
    """Stateless helper that extracts operation metadata from a single code line.

    Tries a priority-ordered list of regex strategies and returns on the first
    match. Receives an optional batch_table context for batch_alter_table blocks.

    Usage:
        extractor = OperationExtractor()
        table, column, rename_to = extractor.extract(code_line, batch_table="my_table")
    """

    def extract(
        self,
        code_part: str,
        batch_table: str | None = None,
    ) -> tuple[str | None, str | None, str | None]:
        """Return (table, column, rename_to) for the given code fragment.

        Args:
            code_part:   A single stripped source line with comments removed.
            batch_table: Table name inferred from the enclosing batch_alter_table
                         context, if any.

        Returns:
            A 3-tuple of (table, column, rename_to). Any element may be None
            if it could not be determined from the line.
        """
        for method in (
            self._batch_alter_header,
            self._batch_op_call,
            self._op_create_table,
            self._op_rename_table,
            self._op_generic,
            self._sql_rename_to,
            self._sql_rename_column,
            self._sql_alter_column,
            self._sql_add_column_with_table,
            self._sql_drop_column_with_table,
            self._sql_alter_drop_rename_table,
            self._sql_create_table,
            self._sql_add_column,
        ):
            result = method(code_part, batch_table)
            if result is not None:
                return result
        return batch_table, None, None

    # -- Extraction strategies (tried in priority order) ---------------------

    @staticmethod
    def _batch_alter_header(
        code: str, _batch: str | None
    ) -> tuple[str, None, None] | None:
        """Match op.batch_alter_table("name") and return the table name."""
        m = re.search(r'(?:op\.)?batch_alter_table\(\s*["\'](\w+)["\']', code)
        return (m.group(1), None, None) if m else None

    @staticmethod
    def _batch_op_call(
        code: str, batch: str | None
    ) -> tuple[str | None, str | None, None] | None:
        """Match batch_op.<operation>(...) calls and return (batch_table, column)."""
        # add_column wraps the name inside sa.Column("name", ...), so the generic
        # first-quoted-arg pattern below would capture "name" from sa.Column instead.
        m = re.search(r'batch_op\.add_column\s*\(.*?["\'](\w+)["\']', code)
        if m:
            return (batch, m.group(1), None)
        m = re.search(r'batch_op\.(?!execute)\w+\(\s*["\'](\w+)["\']\s*[,)]', code)
        return (batch, m.group(1), None) if m else None

    @staticmethod
    def _op_create_table(
        code: str, _batch: str | None
    ) -> tuple[str, None, None] | None:
        """Match op.create_table("name") and return the new table name."""
        if not re.search(r'op\.create_table\s*\(', code):
            return None
        m = re.search(r'op\.create_table\s*\(\s*["\'](\w+)["\']', code)
        return (m.group(1), None, None) if m else None

    @staticmethod
    def _op_rename_table(
        code: str, _batch: str | None
    ) -> tuple[str, None, str] | None:
        """Match op.rename_table("old", "new") and return (old_name, None, new_name)."""
        m = re.search(
            r'op\.rename_table\s*\(\s*["\'](\w+)["\'],\s*["\'](\w+)["\']', code
        )
        return (m.group(1), None, m.group(2)) if m else None

    @staticmethod
    def _op_generic(
        code: str, _batch: str | None
    ) -> tuple[str, str | None, None] | None:
        """Match generic op.<verb>("table"[, col_expr]) and return (table, column).

        The optional second argument is either a bare string "col" or a callable
        wrapping it such as sa.Column("col", ...). Both forms are captured.
        """
        m = re.search(
            r'op\.(?!execute)\w+\(\s*["\'](\w+)["\']'
            r'(?:,\s*(?:(?:\w+\.)*\w+\(\s*["\'](\w+)["\']|["\'](\w+)["\']))?',
            code,
        )
        if not m:
            return None
        return (m.group(1), m.group(2) or m.group(3), None)

    @staticmethod
    def _sql_rename_to(
        code: str, _batch: str | None
    ) -> tuple[str, None, str] | None:
        """Match ALTER TABLE t RENAME TO new_name."""
        m = re.search(
            r'ALTER\s+TABLE\s+(?:\w+\.)?(\w+)\s+RENAME\s+TO\s+(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), None, m.group(2)) if m else None

    @staticmethod
    def _sql_rename_column(
        code: str, _batch: str | None
    ) -> tuple[str, str, str] | None:
        """Match <ALTER|DROP|RENAME> TABLE t RENAME COLUMN old TO new."""
        m = re.search(
            r'(?:ALTER|DROP|RENAME)\s+TABLE\s+(?:\w+\.)?(\w+)'
            r'\s+RENAME\s+COLUMN\s+(\w+)\s+TO\s+(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), m.group(2), m.group(3)) if m else None

    @staticmethod
    def _sql_alter_column(
        code: str, _batch: str | None
    ) -> tuple[str, str, None] | None:
        """Match ALTER TABLE t ALTER COLUMN c."""
        m = re.search(
            r'ALTER\s+TABLE\s+(?:\w+\.)?(\w+)\s+ALTER\s+COLUMN\s+(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), m.group(2), None) if m else None

    @staticmethod
    def _sql_add_column_with_table(
        code: str, _batch: str | None
    ) -> tuple[str, str, None] | None:
        """Match ALTER TABLE t ADD COLUMN c, capturing both table and column."""
        m = re.search(
            r'ALTER\s+TABLE\s+(?:\w+\.)?(\w+)\s+ADD\s+COLUMN\s+(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), m.group(2), None) if m else None

    @staticmethod
    def _sql_drop_column_with_table(
        code: str, _batch: str | None
    ) -> tuple[str, str, None] | None:
        """Match ALTER TABLE t DROP COLUMN c, capturing both table and column."""
        m = re.search(
            r'ALTER\s+TABLE\s+(?:\w+\.)?(\w+)\s+DROP\s+COLUMN\s+(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), m.group(2), None) if m else None

    @staticmethod
    def _sql_alter_drop_rename_table(
        code: str, _batch: str | None
    ) -> tuple[str, None, None] | None:
        """Match <ALTER|DROP|RENAME> TABLE t, returning the table name only.

        Used as a fallback when no column or rename target could be extracted
        by the more specific strategies above.
        """
        m = re.search(
            r'(?:ALTER|DROP|RENAME)\s+TABLE\s+(?:\w+\.)?(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), None, None) if m else None

    @staticmethod
    def _sql_create_table(
        code: str, _batch: str | None
    ) -> tuple[str, None, None] | None:
        """Match CREATE TABLE t and return the table name."""
        m = re.search(r'CREATE\s+TABLE\s+(?:\w+\.)?(\w+)', code, re.IGNORECASE)
        return (m.group(1), None, None) if m else None

    @staticmethod
    def _sql_add_column(
        code: str, batch: str | None
    ) -> tuple[str | None, str, None] | None:
        """Match ADD COLUMN c without an explicit table, falling back to batch context."""
        m = re.search(r'ADD\s+COLUMN\s+(\w+)', code, re.IGNORECASE)
        return (batch, m.group(1), None) if m else None


# ---------------------------------------------------------------------------
# MigrationFile — parses one Alembic migration *.py file
# ---------------------------------------------------------------------------

class MigrationFile:
    """Parses a single Alembic migration file and yields its detected operations.

    Only the upgrade() function body is scanned. Parsing stops at downgrade().
    Supports both direct op.* calls and batch_alter_table context blocks.

    Usage:
        mf = MigrationFile("versions/abc123_add_column.py")
        for op in mf.iter_ops(level="important"):
            print(op.format())
    """

    _extractor = OperationExtractor()

    def __init__(self, path: str | pathlib.Path) -> None:
        self.path = pathlib.Path(path)
        # Revision hash is the second underscore-separated token in the filename stem
        self.hash = self.path.stem.split("_")[1]

    def iter_ops(self, level: str = "important") -> Iterator[MigrationOp]:
        """Yield MigrationOp instances for every detected operation in upgrade().

        Args:
            level: Either "important" (destructive ops) or "notable" (additive ops).

        Raises:
            Exception: Re-raises any parse error after logging it to stderr.
        """
        keywords = _IMPORTANT_KEYWORDS if level == "important" else _NOTABLE_KEYWORDS
        try:
            yield from self._scan(keywords)
        except Exception as exc:
            print(f"Could not parse {self.path}: {exc}", file=sys.stderr)
            raise

    def _scan(self, keywords: tuple[str, ...]) -> Iterator[MigrationOp]:
        """Scan the file line by line and yield one MigrationOp per detected keyword."""
        in_upgrade = False
        batch_table: str | None = None

        with open(self.path, encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()

                # Track entry/exit of the upgrade() and downgrade() functions
                if stripped.startswith("def upgrade("):
                    in_upgrade = True
                    continue
                if stripped.startswith("def downgrade("):
                    in_upgrade = False
                    batch_table = None
                    continue
                if not in_upgrade:
                    continue

                # Strip inline comments before any keyword or regex matching
                code_part = line.split("#")[0]
                if not code_part.strip():
                    continue

                # Update batch_alter_table context: enter on match, exit on dedent
                bm = re.search(
                    r'(?:op\.)?batch_alter_table\(\s*["\'](\w+)["\']', code_part
                )
                if bm:
                    batch_table = bm.group(1)
                elif batch_table and not line.startswith((" ", "\t")):
                    batch_table = None

                # Collect distinct OpKinds matched on this line
                seen_kinds: list[OpKind] = []
                for kw in keywords:
                    if kw in code_part:
                        kind = _KEYWORD_MAP[kw]
                        if kind not in seen_kinds:
                            seen_kinds.append(kind)

                for kind in seen_kinds:
                    table, column, rename_to = self._extractor.extract(
                        code_part, batch_table=batch_table
                    )
                    yield MigrationOp(
                        hash=self.hash,
                        kind=kind,
                        table=table,
                        column=column,
                        rename_to=rename_to,
                    )


# ---------------------------------------------------------------------------
# EnvReport — filters and formats operations for a single deployment environment
# ---------------------------------------------------------------------------

@dataclass
class EnvReport:
    """Holds the filtered operations for one environment and renders Slack alerts.

    Operations are split into two buckets:
    - important: destructive changes on tables present in this environment
    - notable:   additive changes, or any CREATE_TABLE regardless of table subset

    Usage:
        report = EnvReport.build(env="prod", all_ops=ops, tables=imported_tables)
        if report.has_changes:
            print(report.render_with_env(sep="\\n"))
    """

    env: str
    important: list[MigrationOp] = field(default_factory=list)
    notable: list[MigrationOp] = field(default_factory=list)

    @classmethod
    def build(
        cls,
        env: str,
        all_ops: list[MigrationOp],
        tables: set[str],
    ) -> EnvReport:
        """Build an EnvReport by filtering ops against the given table subset.

        Args:
            env:     Logical environment label (e.g. "prod", "stg").
            all_ops: Full list of operations parsed from all migration files.
            tables:  Set of SQL table names imported in this environment.

        Returns:
            A populated EnvReport with ops split into important/notable buckets.
        """
        report = cls(env=env)
        for op in all_ops:
            if op.kind.is_important and op.matches_subset(tables):
                report.important.append(op)
            elif op.kind.is_notable and op.should_notify(tables):
                report.notable.append(op)
        return report

    @property
    def has_changes(self) -> bool:
        """Return True if there is at least one important or notable operation."""
        return bool(self.important or self.notable)

    def _get_team_mentions(level: str) -> str:
        """Return Slack mentions for all teams relevant to a given level (important/notable)."""
        teams = NOTIFICATION_MATRIX.get(level, set())
        if not teams:
            return ""
        return " ".join(team.fmt_slack_mention() for team in teams)

    def render(self, sep: str = r"\n", no_ping: bool = False) -> str:
        """Render this report as a Slack mrkdwn-formatted string.

        Args:
            sep: Line separator. Defaults to the two-character literal ``\\n``
                 which survives GitHub Actions output encoding. Pass ``"\\n"``
                 (actual newline) for local/terminal output.
            no_ping: When True, disable Slack team mentions in output.

        Returns:
            A Slack-formatted multi-line string, or an empty string if no changes.
        """
        lines: list[str] = []
        if self.important:
            mentions = "" if no_ping else self._get_team_mentions("important")
            ping = f" {mentions}" if mentions else ""
            lines.append(f":warning: *Migrations importantes*{ping}")
            lines.extend(f">*{op.format()}*" for op in self.important)
        if self.notable:
            if lines:
                lines.append("")
            mentions = "" if no_ping else self._get_team_mentions("notable")
            ping = f" {mentions}" if mentions else ""
            lines.append(f":rotating_light: *Migrations notables*{ping}")
            lines.extend(f">{op.format()}" for op in self.notable)
        return sep.join(lines)

    def render_with_env(self, sep: str = r"\n", no_ping: bool = False) -> str:
        """Render this report prefixed with a bold environment label.

        Args:
            sep: Line separator forwarded to render(). See render() for details.
            no_ping: When True, disable Slack team mentions in output.

        Returns:
            A Slack-formatted string with an environment header prepended.
        """
        return f"*[{self.env.upper()}]*{sep}{self.render(sep=sep, no_ping=no_ping)}"


# ---------------------------------------------------------------------------
# TableFetcher — retrieves SQL table names imported for a given GitHub branch
# ---------------------------------------------------------------------------

class TableFetcher:
    """Fetches the set of SQL table names imported for a given GitHub branch.

    Queries the GitHub Trees API recursively and extracts table names from
    .sql filenames found under the configured SQL prefix path, excluding any
    files inside subfolders listed in excluded_subfolders.

    Usage:
        fetcher = TableFetcher()
        tables = fetcher.fetch("production")
    """

    def __init__(
        self,
        repo_tree_url: str = REPO_TREE_URL,
        sql_prefix: str = SQL_PREFIX,
        excluded_subfolders: frozenset[str] = EXCLUDED_SUBFOLDERS,
    ) -> None:
        self._repo_tree_url = repo_tree_url
        self._sql_prefix = sql_prefix
        self._excluded = excluded_subfolders

    def fetch(self, branch: str) -> set[str]:
        """Return the set of table names imported on the given branch.

        Args:
            branch: GitHub branch name (e.g. "production", "master").

        Returns:
            A set of table name strings derived from .sql filenames,
            with the .sql extension stripped.
        """
        url = f"{self._repo_tree_url}{branch}?recursive=1"
        with urllib.request.urlopen(url) as response:
            tree = json.load(response)["tree"]
        return {
            item["path"].split("/")[-1].replace(".sql", "")
            for item in tree
            if item["path"].startswith(self._sql_prefix)
            and item["path"].endswith(".sql")
            and not any(
                f"/{folder}/" in item["path"] for folder in self._excluded
            )
        }


# ---------------------------------------------------------------------------
# ChangeDetector — top-level orchestrator for the full detection pipeline
# ---------------------------------------------------------------------------

class ChangeDetector:
    """Orchestrates the full migration change-detection pipeline.

    Steps:
        1. Parse all migration files into a flat list of MigrationOp instances.
        2. Fetch the set of imported tables per branch via TableFetcher.
        3. Build an EnvReport for each environment.
        4. Return only reports that contain at least one change.

    Usage:
        detector = ChangeDetector()
        reports = detector.run(["versions/abc_add_col.py", "versions/def_drop_tbl.py"])
        for report in reports:
            print(report.render_with_env(sep="\\n"))
    """

    def __init__(
        self,
        branch_env: dict[str, str] = BRANCH_ENV,
        fetcher: TableFetcher | None = None,
    ) -> None:
        self._branch_env = branch_env
        self._fetcher = fetcher or TableFetcher()

    def run(self, file_paths: list[str]) -> list[EnvReport]:
        """Run the full pipeline and return non-empty EnvReports.

        Args:
            file_paths: Paths to Alembic migration .py files to analyse.

        Returns:
            A list of EnvReport instances, one per environment that has changes.
        """
        all_ops = self._collect_ops(file_paths)
        reports: list[EnvReport] = []
        for branch, env in self._branch_env.items():
            tables = self._fetcher.fetch(branch)
            print(
                f"Checked against {env} imported tables: {tables}",
                file=sys.stderr,
            )
            report = EnvReport.build(env=env, all_ops=all_ops, tables=tables)
            if report.has_changes:
                reports.append(report)
        return reports

    @staticmethod
    def _collect_ops(file_paths: list[str]) -> list[MigrationOp]:
        """Parse all migration files and return a flat list of all detected ops.

        Args:
            file_paths: Paths to Alembic migration .py files.

        Returns:
            A flat list of MigrationOp instances across all files and severity levels.
        """
        ops: list[MigrationOp] = []
        for path in file_paths:
            mf = MigrationFile(path)
            ops.extend(mf.iter_ops("important"))
            ops.extend(mf.iter_ops("notable"))
        return ops


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(file_names: list[str], debug: bool = False, no_ping: bool = False) -> None:
    """Run change detection and print Slack-formatted alerts for changed environments.

    Args:
        file_names: Paths to Alembic migration .py files to analyse.
        debug:      When True, print per-environment filter details to stderr.
        no_ping:    When True, disable Slack team mentions in output.
    """
    all_ops = ChangeDetector._collect_ops(file_names)

    if debug:
        print("=== Detected ops (before env filter) ===", file=sys.stderr)
        for op in all_ops:
            print(f"  [{op.kind.value}] table={op.table!r} column={op.column!r}", file=sys.stderr)
        print(file=sys.stderr)

    reports: list[EnvReport] = []
    fetcher = TableFetcher()

    for branch, env in BRANCH_ENV.items():
        tables = fetcher.fetch(branch)

        if debug:
            print(f"=== [{env}] imported tables ({len(tables)}) ===", file=sys.stderr)
            passing  = [op for op in all_ops if op.should_notify(tables)]
            filtered = [op for op in all_ops if not op.should_notify(tables)]
            print(f"  passing : {[op.kind.value + ':' + str(op.table) for op in passing]}", file=sys.stderr)
            print(f"  filtered: {[op.kind.value + ':' + str(op.table) for op in filtered]}", file=sys.stderr)
            print(file=sys.stderr)

        report = EnvReport.build(env=env, all_ops=all_ops, tables=tables)
        if report.has_changes:
            reports.append(report)

    if reports:
        print((r"\n" + r"\n").join(r.render_with_env(no_ping=no_ping) for r in reports))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Detect significant Alembic migration operations and alert per environment."
    )
    parser.add_argument("files", nargs="+", type=str, help="Alembic migration .py files to analyse")
    parser.add_argument("--debug", action="store_true", help="Print per-env filter details to stderr")
    parser.add_argument("--no-ping", dest="no_ping", action="store_false", help="Disable Slack team mentions in output")
    parser.set_defaults(no_ping=False)
    args = parser.parse_args()
    main(file_names=args.files, debug=args.debug, no_ping=args.no_ping)
