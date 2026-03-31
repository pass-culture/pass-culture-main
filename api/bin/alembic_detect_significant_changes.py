"""
alembic_detect_significant_changes v2 — OOP edition
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
# Constants
# ---------------------------------------------------------------------------

REPO_TREE_URL = "https://api.github.com/repos/pass-culture/data-gcp/git/trees/"
SQL_PREFIX = "orchestration/dags/dependencies/applicative_database/sql/"
EXCLUDED_SUBFOLDERS = frozenset(["history"])

BRANCH_ENV: dict[str, str] = {
    "production": "prod",
    "master": "stg",
    "test-fake-table": "fake-env",
}


# ---------------------------------------------------------------------------
# OpKind — the canonical set of detectable operation types
# ---------------------------------------------------------------------------

class OpKind(str, Enum):
    """Normalised operation names used throughout the pipeline."""
    ADD_COLUMN    = "add_column"
    ALTER_TYPE    = "alter_type"
    CREATE_TABLE  = "create_table"
    DROP_COLUMN   = "drop_column"
    DROP_TABLE    = "drop_table"
    RENAME_COLUMN = "rename_column"
    RENAME_TABLE  = "rename_table"

    @property
    def is_important(self) -> bool:
        return self in {
            OpKind.ALTER_TYPE,
            OpKind.DROP_COLUMN,
            OpKind.DROP_TABLE,
            OpKind.RENAME_COLUMN,
            OpKind.RENAME_TABLE,
        }

    @property
    def is_notable(self) -> bool:
        return self in {OpKind.ADD_COLUMN, OpKind.CREATE_TABLE}

    @property
    def always_notify(self) -> bool:
        """True when the op should be reported regardless of the table subset."""
        return self is OpKind.CREATE_TABLE


# Keyword → OpKind mapping (all the raw strings that appear in migration code)
_KEYWORD_MAP: dict[str, OpKind] = {
    # important
    "drop_column":    OpKind.DROP_COLUMN,
    "DROP COLUMN":    OpKind.DROP_COLUMN,
    "alter_column":   OpKind.ALTER_TYPE,
    "ALTER COLUMN":   OpKind.ALTER_TYPE,
    "alter_type":     OpKind.ALTER_TYPE,
    "ALTER TYPE":     OpKind.ALTER_TYPE,
    "drop_table":     OpKind.DROP_TABLE,
    "DROP TABLE":     OpKind.DROP_TABLE,
    "rename_table":   OpKind.RENAME_TABLE,
    "RENAME TO":      OpKind.RENAME_TABLE,
    "new_column_name": OpKind.RENAME_COLUMN,
    "RENAME COLUMN":  OpKind.RENAME_COLUMN,
    # notable
    "add_column":     OpKind.ADD_COLUMN,
    "ADD COLUMN":     OpKind.ADD_COLUMN,
    "create_table":   OpKind.CREATE_TABLE,
    "CREATE TABLE":   OpKind.CREATE_TABLE,
}

_IMPORTANT_KEYWORDS = tuple(k for k, v in _KEYWORD_MAP.items() if v.is_important)
_NOTABLE_KEYWORDS   = tuple(k for k, v in _KEYWORD_MAP.items() if v.is_notable)


# ---------------------------------------------------------------------------
# MigrationOp — the core data object
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MigrationOp:
    """A single detected operation inside a migration's upgrade() block."""
    hash: str
    kind: OpKind
    table: str | None
    column: str | None
    rename_to: str | None

    def format(self) -> str:
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
        return self.table in tables

    def should_notify(self, tables: set[str]) -> bool:
        return self.kind.always_notify or self.matches_subset(tables)


# ---------------------------------------------------------------------------
# OperationExtractor — regex waterfall for table/column/rename_to
# ---------------------------------------------------------------------------

class OperationExtractor:
    """
    Stateless helper: given a stripped code line (and an optional batch_table
    context), returns (table, column, rename_to) via a priority-ordered regex
    waterfall.
    """

    def extract(
        self,
        code_part: str,
        batch_table: str | None = None,
    ) -> tuple[str | None, str | None, str | None]:
        """Return (table, column, rename_to)."""
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

    # -- individual extractors -----------------------------------------------

    @staticmethod
    def _batch_alter_header(
        code: str, _batch: str | None
    ) -> tuple[str, None, None] | None:
        m = re.search(r'(?:op\.)?batch_alter_table\(\s*["\'](\w+)["\']', code)
        return (m.group(1), None, None) if m else None

    @staticmethod
    @staticmethod
    def _batch_op_call(
        code: str, batch: str | None
    ) -> tuple[str | None, str | None, None] | None:
        # batch_op.add_column(sa.Column("name", ...)) — grab first quoted string
        m = re.search(r'batch_op\.add_column\s*\(.*?["\'](\w+)["\']', code)
        if m:
            return (batch, m.group(1), None)
        # batch_op.drop_column("name") / batch_op.alter_column("name", ...)
        m = re.search(r'batch_op\.(?!execute)\w+\(\s*["\'](\w+)["\']\s*[,)]', code)
        return (batch, m.group(1), None) if m else None
    @staticmethod
    def _op_create_table(
        code: str, _batch: str | None
    ) -> tuple[str, None, None] | None:
        if not re.search(r'op\.create_table\s*\(', code):
            return None
        m = re.search(r'op\.create_table\s*\(\s*["\'](\w+)["\']', code)
        return (m.group(1), None, None) if m else None

    @staticmethod
    def _op_rename_table(
        code: str, _batch: str | None
    ) -> tuple[str, None, str] | None:
        m = re.search(
            r'op\.rename_table\s*\(\s*["\'](\w+)["\'],\s*["\'](\w+)["\']', code
        )
        return (m.group(1), None, m.group(2)) if m else None

    @staticmethod
    def _op_generic(
        code: str, _batch: str | None
    ) -> tuple[str, str | None, None] | None:
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
        m = re.search(
            r'ALTER\s+TABLE\s+(?:\w+\.)?(\w+)\s+RENAME\s+TO\s+(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), None, m.group(2)) if m else None

    @staticmethod
    def _sql_rename_column(
        code: str, _batch: str | None
    ) -> tuple[str, str, str] | None:
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
        m = re.search(
            r'ALTER\s+TABLE\s+(?:\w+\.)?(\w+)\s+ALTER\s+COLUMN\s+(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), m.group(2), None) if m else None

    @staticmethod
    def _sql_add_column_with_table(
        code: str, _batch: str | None
    ) -> tuple[str, str, None] | None:
        """ALTER TABLE t ADD COLUMN c ... — captures both table and column."""
        m = re.search(
            r'ALTER\s+TABLE\s+(?:\w+\.)?(\w+)\s+ADD\s+COLUMN\s+(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), m.group(2), None) if m else None

    @staticmethod
    def _sql_drop_column_with_table(
        code: str, _batch: str | None
    ) -> tuple[str, str, None] | None:
        """ALTER TABLE t DROP COLUMN c — captures both table and column."""
        m = re.search(
            r'ALTER\s+TABLE\s+(?:\w+\.)?(\w+)\s+DROP\s+COLUMN\s+(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), m.group(2), None) if m else None

    @staticmethod
    def _sql_alter_drop_rename_table(
        code: str, _batch: str | None
    ) -> tuple[str, None, None] | None:
        m = re.search(
            r'(?:ALTER|DROP|RENAME)\s+TABLE\s+(?:\w+\.)?(\w+)',
            code, re.IGNORECASE,
        )
        return (m.group(1), None, None) if m else None

    @staticmethod
    def _sql_create_table(
        code: str, _batch: str | None
    ) -> tuple[str, None, None] | None:
        m = re.search(r'CREATE\s+TABLE\s+(?:\w+\.)?(\w+)', code, re.IGNORECASE)
        return (m.group(1), None, None) if m else None

    @staticmethod
    def _sql_add_column(
        code: str, batch: str | None
    ) -> tuple[str | None, str, None] | None:
        m = re.search(r'ADD\s+COLUMN\s+(\w+)', code, re.IGNORECASE)
        return (batch, m.group(1), None) if m else None


# ---------------------------------------------------------------------------
# MigrationFile — parses one *.py migration file
# ---------------------------------------------------------------------------

class MigrationFile:
    """
    Parses a single Alembic migration file and exposes its detected ops.

    Usage:
        mf = MigrationFile(path)
        for op in mf.iter_ops(level="important"):
            ...
    """

    _extractor = OperationExtractor()

    def __init__(self, path: str | pathlib.Path) -> None:
        self.path = pathlib.Path(path)
        self.hash = self.path.stem.split("_")[1]

    def iter_ops(self, level: str = "important") -> Iterator[MigrationOp]:
        """Yield MigrationOp for every detected operation in upgrade()."""
        keywords = _IMPORTANT_KEYWORDS if level == "important" else _NOTABLE_KEYWORDS
        try:
            yield from self._scan(keywords)
        except Exception as exc:
            print(f"Could not parse {self.path}: {exc}", file=sys.stderr)
            raise

    def _scan(self, keywords: tuple[str, ...]) -> Iterator[MigrationOp]:
        in_upgrade = False
        batch_table: str | None = None

        with open(self.path, encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()

                if stripped.startswith("def upgrade("):
                    in_upgrade = True
                    continue
                if stripped.startswith("def downgrade("):
                    in_upgrade = False
                    batch_table = None
                    continue
                if not in_upgrade:
                    continue

                code_part = line.split("#")[0]
                if not code_part.strip():
                    continue

                # Maintain batch_alter_table context
                bm = re.search(
                    r'(?:op\.)?batch_alter_table\(\s*["\'](\w+)["\']', code_part
                )
                if bm:
                    batch_table = bm.group(1)
                elif batch_table and not line.startswith((" ", "\t")):
                    batch_table = None

                # Deduplicate op kinds per line
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
# EnvReport — filters and formats ops for one environment
# ---------------------------------------------------------------------------

@dataclass
class EnvReport:
    """
    Holds the filtered operations for a single environment (prod/stg/fake-env)
    and knows how to render itself as an alert string.
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
        report = cls(env=env)
        for op in all_ops:
            if op.kind.is_important and op.matches_subset(tables):
                report.important.append(op)
            elif op.kind.is_notable and op.should_notify(tables):
                report.notable.append(op)
        return report

    @property
    def has_changes(self) -> bool:
        return bool(self.important or self.notable)

    def render(self, sep: str = r"\n") -> str:
        """
        Render using Slack mrkdwn. Default sep is the two-char ``\n`` escape
        which survives GitHub Actions output encoding. Pass ``"\n"`` for local output.
        """
        lines: list[str] = []
        if self.important:
            lines.append(":warning: *Migrations importantes*")
            lines.extend(f">*{op.format()}*" for op in self.important)
        if self.notable:
            if lines:
                lines.append("")
            lines.append(":rotating_light: *Migrations notables*")
            lines.extend(f">{op.format()}" for op in self.notable)
        return sep.join(lines)

    def render_with_env(self, sep: str = r"\n") -> str:
        return f"*[{self.env.upper()}]*{sep}{self.render(sep=sep)}"

# ---------------------------------------------------------------------------
# TableFetcher — retrieves imported table names from GitHub
# ---------------------------------------------------------------------------

class TableFetcher:
    """Fetches the set of SQL table names imported for a given branch."""

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
# ChangeDetector — orchestrates the full pipeline
# ---------------------------------------------------------------------------

class ChangeDetector:
    """
    Top-level orchestrator.

    1. Parses all migration files into MigrationOp lists.
    2. Fetches imported tables per branch via TableFetcher.
    3. Builds an EnvReport per environment.
    4. Returns non-empty reports.
    """

    def __init__(
        self,
        branch_env: dict[str, str] = BRANCH_ENV,
        fetcher: TableFetcher | None = None,
    ) -> None:
        self._branch_env = branch_env
        self._fetcher = fetcher or TableFetcher()

    def run(self, file_paths: list[str]) -> list[EnvReport]:
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
        ops: list[MigrationOp] = []
        for path in file_paths:
            mf = MigrationFile(path)
            ops.extend(mf.iter_ops("important"))
            ops.extend(mf.iter_ops("notable"))
        return ops


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(file_names: list[str], debug: bool = False) -> None:
    detector = ChangeDetector()

    # Collect all ops once for debug output
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
            passing = [op for op in all_ops if op.should_notify(tables)]
            filtered = [op for op in all_ops if not op.should_notify(tables)]
            print(f"  passing : {[op.kind.value + ':' + str(op.table) for op in passing]}", file=sys.stderr)
            print(f"  filtered: {[op.kind.value + ':' + str(op.table) for op in filtered]}", file=sys.stderr)
            print(file=sys.stderr)
        report = EnvReport.build(env=env, all_ops=all_ops, tables=tables)
        if report.has_changes:
            reports.append(report)

    if reports:
        print((r"\n" + r"\n").join(r.render_with_env() for r in reports))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", type=str)
    parser.add_argument("--debug", action="store_true", help="Print per-env filter details to stderr")
    args = parser.parse_args()
    main(file_names=args.files, debug=args.debug)