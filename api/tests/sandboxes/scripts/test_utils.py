from unittest import mock

import pytest

from pcapi.sandboxes.scripts.utils import helpers


def test_skip_steps_without_decorator_without_manager():
    func = mock.MagicMock()

    def my_step():
        func()

    assert helpers.STEPS_SKIP.steps_to_skip == []
    my_step()

    func.assert_called_once()
    assert helpers.STEPS_SKIP.steps_to_skip == []


@pytest.mark.parametrize("to_skip", (None, [], ["something_else"], ["my_step"]))
def test_skip_steps_without_decorator_with_manager(to_skip):
    func = mock.MagicMock()

    def my_step():
        func()

    assert helpers.STEPS_SKIP.steps_to_skip == []
    with helpers.skip_steps(steps=to_skip):
        assert helpers.STEPS_SKIP.steps_to_skip == ([] if to_skip is None else to_skip)
        my_step()

    func.assert_called_once()
    assert helpers.STEPS_SKIP.steps_to_skip == []


def test_skip_steps_with_decorator_without_manager():
    func = mock.MagicMock()

    @helpers.log_func_duration
    def my_step():
        func()

    assert helpers.STEPS_SKIP.steps_to_skip == []
    my_step()

    func.assert_called_once()
    assert helpers.STEPS_SKIP.steps_to_skip == []


@pytest.mark.parametrize("to_skip", (None, [], ["something_else"]))
def test_skip_steps_with_decorator_with_manager_not_skipped(to_skip):
    func = mock.MagicMock()

    @helpers.log_func_duration
    def my_step():
        func()

    assert helpers.STEPS_SKIP.steps_to_skip == []
    with helpers.skip_steps(steps=to_skip):
        assert helpers.STEPS_SKIP.steps_to_skip == ([] if to_skip is None else to_skip)
        my_step()

    func.assert_called_once()
    assert helpers.STEPS_SKIP.steps_to_skip == []


def test_skip_steps_with_decorator_with_manager_skipped():
    func = mock.MagicMock()

    @helpers.log_func_duration
    def my_step():
        func()

    assert helpers.STEPS_SKIP.steps_to_skip == []
    with helpers.skip_steps(steps=["my_step"]):
        assert helpers.STEPS_SKIP.steps_to_skip == ["my_step"]
        my_step()

    func.assert_not_called()
    assert helpers.STEPS_SKIP.steps_to_skip == []
