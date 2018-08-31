from domain.build_recommendations import build_mixed_recommendations
from utils.test_utils import create_recommendation


def test_build_mixed_recommendations_with_only_created_recommendations():
    # given
    created_recommendations = [create_recommendation(id=1), create_recommendation(id=2)]
    read_recommendations = []
    unread_recommendations = []

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [1, 2]


def test_build_mixed_recommendations_with_created_recommendations_and_unread_but_none_read():
    # given
    created_recommendations = [create_recommendation(id=1), create_recommendation(id=2)]
    read_recommendations = []
    unread_recommendations = [create_recommendation(id=3), create_recommendation(id=4)]

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [1, 2, 3, 4]


def test_build_mixed_recommendations_with_created_recommendations_and_read_but_none_unread():
    # given
    created_recommendations = [create_recommendation(id=1), create_recommendation(id=2)]
    read_recommendations = [create_recommendation(id=3), create_recommendation(id=4)]
    unread_recommendations = []

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [1, 2, 3, 4]


def test_build_mixed_recommendations_with_only_read_recommendations_and_none_created():
    # given
    created_recommendations = []
    read_recommendations = [create_recommendation(id=1), create_recommendation(id=2)]
    unread_recommendations = []

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [1, 2]


def test_build_mixed_recommendations_with_only_unread_recommendations_and_none_created():
    # given
    created_recommendations = []
    read_recommendations = []
    unread_recommendations = [create_recommendation(id=1), create_recommendation(id=2)]

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [1, 2]


def test_build_mixed_recommendations_with_read_recommendations_and_unread_but_none_created():
    # given
    created_recommendations = []
    read_recommendations = [create_recommendation(id=1), create_recommendation(id=2)]
    unread_recommendations = [create_recommendation(id=3), create_recommendation(id=4)]

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [3, 4, 1, 2]


def test_build_mixed_recommendations_with_all_sorts_of_recommendations():
    # given
    created_recommendations = [create_recommendation(id=5), create_recommendation(id=6)]
    read_recommendations = [create_recommendation(id=1), create_recommendation(id=2)]
    unread_recommendations = [create_recommendation(id=3), create_recommendation(id=4)]

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [5, 6, 3, 4, 1, 2]
