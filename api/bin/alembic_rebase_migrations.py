#!/usr/bin/env python
"""Rebase migrations and update Alembic conflict detection file upon a
failing Git rebase off of master.

If your feature branch contains new Alembic migrations and the master
branch has more recent migrations, you'll have an error when rebasing
off of master, something like:

    Auto-merging api/alembic_version_conflict_detection.txt
    CONFLICT (content): Merge conflict in api/alembic_version_conflict_detection.txt
    error: could not apply 679ecbc01c...

You must then update this file and the "down_revision" variable in the
first "pre" and/or "post" migration(s) of your branch. This is prone to
error and cumbersome. This tool does everything.

Usage:

    $ git rebase master
    Fusion automatique de api/alembic_version_conflict_detection.txt
    CONFLIT (contenu) : Conflit de fusion dans api/alembic_version_conflict_detection.txt
    erreur : impossible d'appliquer 42e2d11e64... (BSR)[API] feat: WIP, DO NOT MERGE: update models (and add migrations)
    astuce : Resolve all conflicts manually, mark them as resolved with
    astuce : "git add/rm <conflicted_files>", then run "git rebase --continue".
    astuce : You can instead skip this commit: run "git rebase --skip".
    astuce : To abort and get back to the state before "git rebase", run "git rebase --abort".
    astuce : Disable this message with "git config advice.mergeConflict false"
    Impossible d'appliquer 42e2d11e64... (BSR)[API] feat: WIP, DO NOT MERGE: update models (and add migrations)

    # Don't panic:
    $ alembic_rebase_migrations
    The conflict on "alembic_version_conflict_detection.txt" has been resolved and some files have been modified, you must "git add" them before continuing the rebase:
    git add api/src/pcapi/alembic/versions/20240619T135321_bd3fa90c7463_add_column_a_first_pre.py;
    git add api/src/pcapi/alembic/versions/20240619T135531_7b9467cdbeec_column_a_not_nullable_post.py;
    git add api/alembic_version_conflict_detection.txt;

    # Do as told and copy and paste the commands:
    $ git add api/src/pcapi/alembic/versions/20240619T135321_bd3fa90c7463_add_column_a_first_pre.py;
    git add api/src/pcapi/alembic/versions/20240619T135531_7b9467cdbeec_column_a_not_nullable_post.py;
    git add api/alembic_version_conflict_detection.txt;

    # Continue the rebase. Here we don't have any conflict left, so:
    $ git rebase --continue

"""

import ast
import dataclasses
import pathlib
import re
import subprocess
import sys


# Paths are relative to root of the git checkout.
ALEMBIC_VERSION_CONFLICT_DETECTION_PATH = pathlib.Path("api/alembic_version_conflict_detection.txt")
ALEMBIC_VERSION_DIR = pathlib.Path("api/src/pcapi/alembic/versions")


@dataclasses.dataclass
class RevisionFile:
    revision: str
    down_revision: str
    down_revision_lineno: int
    path: pathlib.Path
    ast_tree: ast.Module


def get_constant_from_migration_file(tree: ast.Module, name: str) -> tuple[str, int]:
    """Return the value of a constant (such as ``revision``) in an
    Alembic migration file, and the line number where it is defined.
    """
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        assert hasattr(node.targets[0], "id")  # help mypy
        if node.targets[0].id == name:
            assert hasattr(node.value, "value")  # help mypy
            return node.value.value, node.lineno
    raise ValueError('Could not find constant "{name}".')


def get_alembic_heads_on_local(git_root: pathlib.Path) -> dict[str, str]:
    """Return a dictionary with the head (last revision) of each
    Alembic branch.
    """
    path = git_root / ALEMBIC_VERSION_CONFLICT_DETECTION_PATH
    lines = [l.strip() for l in path.read_text().splitlines()]
    # Expected format:
    #     <<<<<< HEAD
    #     f830372aa947 (pre) (head)
    #     0b8e5f65a615 (post) (head)
    #     =======
    #     e7a96231bff2 (pre) (head)
    #     7b9467cdbeec (post) (head)
    #     >>>>>>> 170f5ed9af (my commit)
    return {"pre": lines[4].split(" ")[0], "post": lines[5].split(" ")[0]}


def get_first_revisions(
    revision_files: dict[str, RevisionFile],
    heads_on_local: dict[str, str],
) -> dict[str, str | None]:
    """Return a dictionary with the first revision(s) that are new in
    the feature branch.

    We do this by finding the _last_ revision on all Alembic branches,
    and then walking backwards in the set of added revision files,
    until we find the first one (for each Alembic branch).
    """
    first_revisions: dict[str, str | None] = {"pre": None, "post": None}
    for alembic_branch in ("pre", "post"):
        revision = heads_on_local[alembic_branch]
        first_revision: str | None = None
        while 1:
            try:
                revision_file = revision_files[revision]
            except KeyError:
                break
            first_revision = revision
            revision = revision_file.down_revision
        first_revisions[alembic_branch] = first_revision
    return first_revisions


def get_revision_files(git_root: pathlib.Path) -> dict[str, RevisionFile]:
    try:
        res = subprocess.run(
            ("git", "diff", "--name-only", "--staged"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        err = "Could not run `git diff` to detect your first migration(s)."
        err += "\n" + exc.stderr.decode("utf-8").strip()
        sys.exit(err)
    text = res.stdout.decode("utf-8")
    revision_files = {}
    for line in text.splitlines():
        path = pathlib.Path(line)
        if not path.is_relative_to(ALEMBIC_VERSION_DIR):
            continue
        path = git_root / path
        ast_tree = ast.parse(path.read_text(), path.name)
        revision, _ = get_constant_from_migration_file(ast_tree, "revision")
        down_revision, down_revision_lineno = get_constant_from_migration_file(ast_tree, "down_revision")
        revision_files[revision] = RevisionFile(
            path=path,
            revision=revision,
            down_revision=down_revision,
            down_revision_lineno=down_revision_lineno,
            ast_tree=ast_tree,
        )
    return revision_files


def update_down_revision(
    path: pathlib.Path,
    lineno: int,
    old_down_revision: str,
    new_down_revision: str,
) -> None:
    # We cannot use `ast.unparse()` because the `ast` module does not
    # preserve comments. We'll use a good old regexp and try to avoid
    # mismatch by only changing a particular line (which we know from
    # the AST).
    text = path.read_text()
    lines = text.splitlines()
    if text.endswith("\n"):  # avoid removing newline at end of file
        lines.append("")
    lines[lineno - 1] = re.sub(old_down_revision, new_down_revision, lines[lineno - 1])
    path.write_text("\n".join(lines))


def update_alembic_version_conflict_detection_file(
    git_root: pathlib.Path,
    heads_on_local: dict[str, str],
) -> None:
    lines = []
    for branch in sorted(heads_on_local, reverse=True):  # pre, post
        lines.append(f"{heads_on_local[branch]} ({branch}) (head)")
    path = git_root / ALEMBIC_VERSION_CONFLICT_DETECTION_PATH
    path.write_text("\n".join(lines) + "\n")


def get_git_checkout_root() -> pathlib.Path:
    path = pathlib.Path.cwd()
    while not (path / ".git").exists():
        path = path.parent
    return path


def get_alembic_heads_on_master() -> dict[str, str]:
    try:
        res = subprocess.run(
            ("git", "show", f"origin/master:{ALEMBIC_VERSION_CONFLICT_DETECTION_PATH}"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        err = "Could not fetch Alembic heads on master."
        err += "\n" + exc.stderr.decode("utf-8").strip()
        sys.exit(err)
    text = res.stdout.decode("utf-8")
    heads: dict[str, str] = {}
    for alembic_branch in ("pre", "post"):
        m = re.search(rf"^(\w+) \({alembic_branch}\) \(head\)", text, re.MULTILINE)
        if not m:
            sys.exit(
                f"Could not extract head for {alembic_branch} branch from {ALEMBIC_VERSION_CONFLICT_DETECTION_PATH}"
            )
        heads[alembic_branch] = m.group(1)
    return heads


def main() -> None:
    git_root = get_git_checkout_root()
    revision_files = get_revision_files(git_root)
    if not revision_files:
        print("No migration files have been detected.")
        return
    heads_on_local = get_alembic_heads_on_local(git_root)
    first_revisions = get_first_revisions(revision_files, heads_on_local)
    heads_on_master = get_alembic_heads_on_master()

    cwd = pathlib.Path.cwd()
    commands = []
    for alembic_branch, first_revision in first_revisions.items():
        if first_revision:
            revision_file = revision_files[first_revision]
            update_down_revision(
                path=revision_file.path,
                lineno=revision_file.down_revision_lineno,
                old_down_revision=revision_file.down_revision,
                new_down_revision=heads_on_master[alembic_branch],
            )
            commands.append(f"git add {revision_file.path.relative_to(cwd)};")
    update_alembic_version_conflict_detection_file(git_root, heads_on_local)
    local_conflict_detection_path = (git_root / ALEMBIC_VERSION_CONFLICT_DETECTION_PATH).relative_to(cwd)
    commands.append(f"git add {local_conflict_detection_path};")

    print(
        f'The conflict on "{ALEMBIC_VERSION_CONFLICT_DETECTION_PATH.name}" has been resolved and some files have been modified, you must "git add" them before continuing the rebase:'
    )
    print("\n".join(commands))


if __name__ == "__main__":
    main()
