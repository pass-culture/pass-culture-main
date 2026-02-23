from unittest import mock

import pytest

from pcapi.sandboxes.scripts.utils import helpers


def test_skip_steps_without_decorator_without_manager():
    func = mock.MagicMock()

    def my_step():
        func()

    assert helpers.STEPS_SELECT.steps_to_skip == []
    assert helpers.STEPS_SELECT.steps_to_run == []
    my_step()

    func.assert_called_once()
    assert helpers.STEPS_SELECT.steps_to_skip == []
    assert helpers.STEPS_SELECT.steps_to_run == []


@pytest.mark.parametrize("to_skip", (None, [], ["something_else"], ["my_step"]))
def test_skip_steps_without_decorator_with_manager(to_skip):
    func = mock.MagicMock()

    def my_step():
        func()

    assert helpers.STEPS_SELECT.steps_to_skip == []
    with helpers.select_steps(steps_to_skip=to_skip, steps_to_run=[]):
        assert helpers.STEPS_SELECT.steps_to_skip == ([] if to_skip is None else to_skip)
        my_step()

    func.assert_called_once()
    assert helpers.STEPS_SELECT.steps_to_skip == []


def test_skip_steps_with_decorator_without_manager():
    func = mock.MagicMock()

    @helpers.log_func_duration
    def my_step():
        func()

    assert helpers.STEPS_SELECT.steps_to_skip == []
    my_step()

    func.assert_called_once()
    assert helpers.STEPS_SELECT.steps_to_skip == []


@pytest.mark.parametrize("to_skip", (None, [], ["something_else"]))
def test_skip_steps_with_decorator_with_manager_not_skipped(to_skip):
    func = mock.MagicMock()

    @helpers.log_func_duration
    def my_step():
        func()

    assert helpers.STEPS_SELECT.steps_to_skip == []
    with helpers.select_steps(steps_to_skip=to_skip, steps_to_run=[]):
        assert helpers.STEPS_SELECT.steps_to_skip == ([] if to_skip is None else to_skip)
        my_step()

    func.assert_called_once()
    assert helpers.STEPS_SELECT.steps_to_skip == []


def test_skip_steps_with_decorator_with_manager_skipped():
    func = mock.MagicMock()

    @helpers.log_func_duration
    def my_step():
        func()

    assert helpers.STEPS_SELECT.steps_to_skip == []
    with helpers.select_steps(steps_to_skip=["my_step"], steps_to_run=[]):
        assert helpers.STEPS_SELECT.steps_to_skip == ["my_step"]
        my_step()

    func.assert_not_called()
    assert helpers.STEPS_SELECT.steps_to_skip == []


def test_select_steps_with_decorator():
    func_1 = mock.MagicMock()
    func_2 = mock.MagicMock()

    @helpers.log_func_duration
    def my_step_1():
        func_1()

    @helpers.log_func_duration
    def my_step_2():
        func_2()

    assert helpers.STEPS_SELECT.steps_to_run == []
    with helpers.select_steps(steps_to_skip=[], steps_to_run=["my_step_2"]):
        assert helpers.STEPS_SELECT.steps_to_run == ["my_step_2"]
        my_step_1()
        my_step_2()

    func_1.assert_not_called()
    func_2.assert_called_once()
    assert helpers.STEPS_SELECT.steps_to_run == []


def test_select_and_skip_error():
    with pytest.raises(ValueError) as ex:
        with helpers.select_steps(steps_to_skip=["test"], steps_to_run=["test"]):
            print("hello")

    assert str(ex.value) == "Only one of steps_to_skip or steps_to_run should be provided"
