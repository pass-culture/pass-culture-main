import click
import pytest

from pcapi.scripts.check_pre_migrations import _get_database_pre_head


class _FakeRevision:
    def __init__(self, branch_labels: tuple[str, ...]) -> None:
        self.branch_labels = branch_labels


class _FakeDirectory:
    def __init__(self, labels_by_head: dict[str, tuple[str, ...]]) -> None:
        self._labels_by_head = labels_by_head

    def get_revision(self, head: str) -> _FakeRevision:
        return _FakeRevision(self._labels_by_head[head])


def test_get_database_pre_head_returns_matching_pre_branch() -> None:
    directory = _FakeDirectory(
        {
            "head-main": ("main",),
            "head-pre": ("pre",),
        }
    )

    database_pre_head = _get_database_pre_head(("head-main", "head-pre"), directory)

    assert database_pre_head == "head-pre"


def test_get_database_pre_head_raises_when_no_heads() -> None:
    directory = _FakeDirectory({})

    with pytest.raises(click.ClickException, match="Could not find any of"):
        _get_database_pre_head((), directory)


def test_get_database_pre_head_raises_when_no_pre_branch_label() -> None:
    directory = _FakeDirectory(
        {
            "head-main": ("main",),
            "head-other": ("other",),
        }
    )

    with pytest.raises(click.ClickException, match="Could not find any of"):
        _get_database_pre_head(("head-main", "head-other"), directory)


def test_get_database_pre_head_raises_when_heads_is_none() -> None:
    directory = _FakeDirectory({})

    with pytest.raises(click.ClickException, match="Could not determine current database migration heads"):
        _get_database_pre_head(None, directory)
