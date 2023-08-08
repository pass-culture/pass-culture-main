import pytest

from pcapi.core.providers.titelive_gtl import get_gtl


@pytest.mark.parametrize(
    "gtl_id, label, level_01, level_02, level_03, level_04",
    (
        ("01000000", "Littérature", "Littérature", None, None, None),
        ("01030000", "Œuvres classiques", "Littérature", "Œuvres classiques", None, None),
        ("01030100", "Antiquité", "Littérature", "Œuvres classiques", "Antiquité", None),
        (
            "01030102",
            "Littérature grecque antique",
            "Littérature",
            "Œuvres classiques",
            "Antiquité",
            "Littérature grecque antique",
        ),
        ("01030103", "Littérature latine", "Littérature", "Œuvres classiques", "Antiquité", "Littérature latine"),
        (
            "01030101",
            "Littérature antique autre",
            "Littérature",
            "Œuvres classiques",
            "Antiquité",
            "Littérature antique autre",
        ),
        ("01030200", "Moyen Age", "Littérature", "Œuvres classiques", "Moyen Age", None),
        ("01030202", "Chanson de geste", "Littérature", "Œuvres classiques", "Moyen Age", "Chanson de geste"),
        ("01030203", "Roman courtois", "Littérature", "Œuvres classiques", "Moyen Age", "Roman courtois"),
        (
            "01030201",
            "Littérature moyenâgeuse autre",
            "Littérature",
            "Œuvres classiques",
            "Moyen Age",
            "Littérature moyenâgeuse autre",
        ),
    ),
)
def test_get_gtl(gtl_id, label, level_01, level_02, level_03, level_04):
    gtl = get_gtl(gtl_id)
    assert gtl["label"] == label
    assert gtl["level_01_code"] == gtl_id[:2]
    assert gtl["level_01_label"] == level_01
    assert gtl["level_02_code"] == gtl_id[2:4]
    assert gtl["level_02_label"] == level_02
    assert gtl["level_03_code"] == gtl_id[4:6]
    assert gtl["level_03_label"] == level_03
    assert gtl["level_04_code"] == gtl_id[6:]
    assert gtl["level_04_label"] == level_04


def test_get_gtl_not_found():
    non_existing_gtl_id = "03040202"
    gtl = get_gtl(non_existing_gtl_id)
    assert gtl is None
