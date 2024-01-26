import pytest

from pcapi.utils import human_ids


def test_humanize():
    assert human_ids.humanize(None) is None
    assert human_ids.humanize(1234) == "ATJA"


def test_dehumanize():
    assert human_ids.dehumanize(None) is None
    assert human_ids.dehumanize("ATJA") == 1234


@pytest.mark.parametrize("value", ("garbage", "é", "---", "   "))
def test_dehumanize_garbage(value):
    with pytest.raises(human_ids.NonDehumanizableId):
        human_ids.dehumanize(value)
