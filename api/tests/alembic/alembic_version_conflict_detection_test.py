import subprocess


def test_versions_are_up_to_date():
    alembic_heads_command = subprocess.run("alembic heads", capture_output=True, shell=True, text=True, check=True)
    alembic_heads = alembic_heads_command.stdout.splitlines()

    try:
        pre_version_line = next(line for line in alembic_heads if "(pre)" in line)
        post_version_line = next(line for line in alembic_heads if "(post)" in line)
    except StopIteration:
        raise AssertionError(
            "`alembic heads` command did not return the expected output. (pre) or (post) version not found."
        )

    pre_version_num = pre_version_line.split(" ")[0]
    post_version_num = post_version_line.split(" ")[0]

    with open("alembic_version_conflict_detection.txt", "r", encoding="utf-8") as content_file:
        output = content_file.read().splitlines()

        try:
            pre_version_line_in_file = next(line for line in output if "(pre)" in line)
            post_version_line_in_file = next(line for line in output if "(post)" in line)
        except StopIteration:
            raise AssertionError(
                "The alembic_version_conflict_detection.txt file is not up to date. (pre) or (post) version not found."
            )

        pre_version_num_in_file = pre_version_line_in_file.split(" ")[0]
        post_version_num_in_file = post_version_line_in_file.split(" ")[0]

    assert pre_version_num == pre_version_num_in_file, (
        "The alembic_version_conflict_detection.txt file is not up to date. Modify pre version to match the database state"
    )

    assert post_version_num == post_version_num_in_file, (
        "The alembic_version_conflict_detection.txt file is not up to date. Modify post version to match the database state"
    )
