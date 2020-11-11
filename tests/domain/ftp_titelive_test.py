import re

from freezegun import freeze_time

from pcapi.domain.titelive import put_today_file_at_end_of_list


@freeze_time("2019-01-03 12:00:00")
def test_put_today_file_at_end_of_list_order_file_as_expected(app):
    # given
    files_list = list(
        [
            "Quotidien01.tit",
            "Quotidien02.tit",
            "Quotidien03.tit",
            "Quotidien04.tit",
            "Quotidien05.tit",
            "Quotidien06.tit",
            "Quotidien07.tit",
        ]
    )

    # when
    ordered_files = put_today_file_at_end_of_list(files_list, re.compile(r"([a-zA-Z]+)(\d+).tit"))

    # then
    assert len(ordered_files) == len(files_list)
    expected_files_list = list(
        [
            "Quotidien04.tit",
            "Quotidien05.tit",
            "Quotidien06.tit",
            "Quotidien07.tit",
            "Quotidien01.tit",
            "Quotidien02.tit",
            "Quotidien03.tit",
        ]
    )
    assert expected_files_list == ordered_files
