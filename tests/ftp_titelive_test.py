import pytest
import re

from freezegun import freeze_time
from utils.ftp_titelive import put_today_file_at_end_of_list


@pytest.mark.standalone
@freeze_time('2019-01-03 12:00:00')
def test_put_today_file_at_end_of_list(app):
    # given
    files_list = list(['Quotidien01.tit',
                       'Quotidien02.tit',
                       'Quotidien03.tit',
                       'Quotidien04.tit',
                       'Quotidien05.tit',
                       'Quotidien06.tit',
                       'Quotidien07.tit'])

    # when
    ordered_files = put_today_file_at_end_of_list(files_list, re.compile('([a-zA-Z]+)(\d+).tit'))

    # then
    assert ordered_files[-1] == 'Quotidien03.tit'
