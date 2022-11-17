from pcapi.models import db


def test_versions_are_up_to_date():
    version_num_rows = db.engine.execute("SELECT version_num FROM alembic_version").fetchall()
    pre_version_num = version_num_rows[0][0]
    post_version_num = version_num_rows[1][0]

    with open("alembic_version_conflict_detection.txt", "r", encoding="utf-8") as content_file:
        output = content_file.read()
    assert (
        output == f"""{pre_version_num} (pre) (head)\n{post_version_num} (post) (head)\n"""
    ), "The alembic_version_conflict_detection.txt file is not up to date. Modify pre and/or post version to match the database state"
