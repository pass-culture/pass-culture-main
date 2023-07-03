from pcapi.core.providers.titelive_utils import COLUMN_INDICES
from pcapi.core.providers.titelive_utils import HEADER_LINES_COUNT
from pcapi.core.providers.titelive_utils import _get_gtls_from_csv_reader


ROWS = [
    ["Niveau 1", "Niveau 2", "Niveau 3", "Niveau 4", "En Bleu = les nouveaux GTL maj en juin 2023"],
    ["Code", "Libellé", "Code", "Libellé", "Code", "Libellé"],
    [
        "12",
        "Parascolaire",
        "25",
        "Langues",
        "10",
        "Français langue étrangère (FLE)",
        "02",
        "Français langue étrangère (FLE) apprentissage",
        "",
        "12251002",
        "Français langue étrangère (FLE) apprentissage",
    ],
    [
        "12",
        "Parascolaire",
        "25",
        "Langues",
        "10",
        "Français langue étrangère (FLE)",
        "03",
        "Français langue étrangère (FLE) lectures",
        "",
        "12251003",
        "Français langue étrangère (FLE) lectures",
    ],
    [
        "12",
        "Parascolaire",
        "25",
        "Langues",
        "10",
        "Français langue étrangère (FLE)",
        "01",
        "Français langue étrangère (FLE) autre",
        "",
        "12251001",
        "Français langue étrangère (FLE) autre",
    ],
    ["12", "Parascolaire", "25", "Langues", "01", "Langues autre", "", "", "", "12250100", "Langues autre"],
    [
        "13",
        "Dictionnaires / Encyclopédies / Documentation",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "13000000",
        "Dictionnaires / Encyclopédies / Documentation",
    ],
    [
        "13",
        "Dictionnaires / Encyclopédies / Documentation",
        "01",
        "Dictionnaires de français",
        "",
        "",
        "",
        "",
        "",
        "13010000",
        "Dictionnaires de français",
    ],
    [
        "13",
        "Dictionnaires / Encyclopédies / Documentation",
        "01",
        "Dictionnaires de français",
        "01",
        "Dictionnaires généralistes",
        "",
        "",
        "",
        "13010100",
        "Dictionnaires généralistes",
    ],
    [
        "13",
        "Dictionnaires / Encyclopédies / Documentation",
        "01",
        "Dictionnaires de français",
        "02",
        "Dictionnaires de langage",
        "",
        "",
        "",
        "13010200",
        "Dictionnaires de langage",
    ],
    [
        "13",
        "Dictionnaires / Encyclopédies / Documentation",
        "01",
        "Dictionnaires de français",
        "03",
        "Dictionnaires scolaires",
        "",
        "",
        "",
        "13010300",
        "Dictionnaires scolaires",
    ],
    [
        "13",
        "Dictionnaires / Encyclopédies / Documentation",
        "02",
        "Encyclopédies",
        "",
        "",
        "",
        "",
        "",
        "13020000",
        "Encyclopédies",
    ],
    [
        "13",
        "Dictionnaires / Encyclopédies / Documentation",
        "02",
        "Encyclopédies",
        "01",
        "Encyclopédies générales",
        "",
        "",
        "",
        "13020100",
        "Encyclopédies générales",
    ],
    [
        "13",
        "Dictionnaires / Encyclopédies / Documentation",
        "02",
        "Encyclopédies",
        "02",
        "Encyclopédies / Dictionnaires thématiques",
        "",
        "",
        "",
        "13020200",
        "Encyclopédies / Dictionnaires thématiques",
    ],
    [
        "13",
        "Dictionnaires / Encyclopédies / Documentation",
        "03",
        "Ouvrages de documentation",
        "",
        "",
        "",
        "",
        "",
        "13030000",
        "Ouvrages de documentation",
    ],
]


def test_get_gtl():
    gtls = _get_gtls_from_csv_reader(ROWS)
    for index, row in enumerate(ROWS):
        if index >= HEADER_LINES_COUNT:
            gtl_id = str(row[COLUMN_INDICES["GTL_ID"]])
            level_01_label = row[COLUMN_INDICES["LEVEL_01_LABEL"]]
            level_02_label = row[COLUMN_INDICES["LEVEL_02_LABEL"]] or None
            level_03_label = row[COLUMN_INDICES["LEVEL_03_LABEL"]] or None
            level_04_label = row[COLUMN_INDICES["LEVEL_04_LABEL"]] or None
            gtl_label = row[COLUMN_INDICES["GTL_LABEL"]]

            assert gtls[gtl_id]["label"] == gtl_label
            assert gtls[gtl_id]["level_01_code"] == gtl_id[:2]
            assert gtls[gtl_id]["level_01_label"] == level_01_label
            assert gtls[gtl_id]["level_02_code"] == gtl_id[2:4]
            assert gtls[gtl_id]["level_02_label"] == level_02_label
            assert gtls[gtl_id]["level_03_code"] == gtl_id[4:6]
            assert gtls[gtl_id]["level_03_label"] == level_03_label
            assert gtls[gtl_id]["level_04_code"] == gtl_id[6:]
            assert gtls[gtl_id]["level_04_label"] == level_04_label
