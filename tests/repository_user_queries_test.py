from datetime import datetime

import pytest
from postgresql_audit.flask import versioning_manager

from models import PcObject
from repository.user_queries import find_users_by_department_and_date_range, find_users_booking_stats_per_department
from tests.conftest import clean_database
from utils.test_utils import create_user


@pytest.mark.standalone
@clean_database
def test_find_user_by_department_and_date_range(app):
    #given
    date_max = '2018-06-06'
    date_min = '2018-05-05'
    department = '34'
    user1 = create_user(email='a@a.f', departement_code='34', date_created=datetime(2018, 5, 10))
    user2 = create_user(email='a@b.f', departement_code='93', date_created=datetime(2018, 5, 10))
    user3 = create_user(email='a@c.f', departement_code='34', date_created=datetime(2018, 4, 10))
    user4 = create_user(email='a@d.f', departement_code='34', date_created=datetime(2018, 9, 10))
    PcObject.check_and_save(user1, user2, user3, user4)

    #when
    users = find_users_by_department_and_date_range(date_max, date_min, department)

    #then

    assert (user1.id, user1.dateCreated, user1.departementCode) in users
    assert (user2.id, user2.dateCreated, user2.departementCode) not in users
    assert (user3.id, user3.dateCreated, user3.departementCode) not in users
    assert (user4.id, user4.dateCreated, user4.departementCode) not in users

# @pytest.mark.standalone
# @clean_database
# def test_find_users_booking_stats_per_department(app):
#     #given
#     time_intervall = 'month'
#     user1 = create_user(email='a@a.f', departement_code='34', date_created=datetime(2018, 5, 10))
#     user2 = create_user(email='a@b.f', departement_code='93', date_created=datetime(2018, 5, 10))
#     user3 = create_user(email='a@c.f', departement_code='34', date_created=datetime(2018, 4, 10))
#     user4 = create_user(email='a@d.f', departement_code='34', date_created=datetime(2018, 9, 10))
#
#
#
#     Activity = versioning_manager.activity_cls
#     activity_1 = Activity()
#     activity_1.issued_at = datetime(2018, 5, 10, 12, 30, 0)
#     activity_1.verb = 'create'
#     PcObject.check_and_save(user1, user2, user3, user4)
#
#     #when
#     users_booking_stats = find_users_booking_stats_per_department(time_intervall)
#
#     #then
#
#     assert (user1.id, user1.dateCreated, user1.departementCode) in users
#     assert (user2.id, user2.dateCreated, user2.departementCode) not in users
#     assert (user3.id, user3.dateCreated, user3.departementCode) not in users
#     assert (user4.id, user4.dateCreated, user4.departementCode) not in users