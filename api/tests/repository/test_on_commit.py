from unittest.mock import MagicMock

from pcapi.repository import atomic
from pcapi.repository import mark_transaction_as_invalid
from pcapi.repository import on_commit


class AtomicTest:
    def test_on_commit_outside_managed_session(self):
        mocked_function = MagicMock()
        on_commit(func=mocked_function)
        mocked_function.assert_called_once()

    def test_on_commit_inside_managed_transaction(self):
        mocked_function = MagicMock()
        with atomic():
            on_commit(func=mocked_function)
        mocked_function.assert_called_once()

    def test_invalid_session_do_not_call_callbacks(self):
        mocked_function = MagicMock()

        @atomic()
        def managed_function():
            on_commit(func=mocked_function)
            mark_transaction_as_invalid()

        managed_function()
        mocked_function.assert_not_called()

    def test_nominal_one_callback(self):
        mocked_function = MagicMock()

        @atomic()
        def managed_function():
            on_commit(func=mocked_function)

        managed_function()
        mocked_function.assert_called_once()

    def test_nominal_two_callback_with_order(self):
        first_callback = MagicMock()
        second_callback = MagicMock()
        call_order = []
        first_callback.side_effect = lambda *a, **kw: call_order.append(1)
        second_callback.side_effect = lambda *a, **kw: call_order.append(2)

        @atomic()
        def managed_function():
            on_commit(func=first_callback)
            on_commit(func=second_callback)

        managed_function()

        first_callback.assert_called_once()
        second_callback.assert_called_once()
        assert call_order == [1, 2]

    def test_stop_at_first_error(self):
        first_callback = MagicMock()
        second_callback = MagicMock()
        first_callback.side_effect = ValueError

        @atomic()
        def managed_function():
            on_commit(func=first_callback)
            on_commit(func=second_callback)

        managed_function()

        first_callback.assert_called_once()
        second_callback.assert_not_called()

    def test_continue_on_error_if_robust(self):
        first_callback = MagicMock()
        second_callback = MagicMock()
        first_callback.side_effect = ValueError

        @atomic()
        def managed_function():
            on_commit(func=first_callback, robust=True)
            on_commit(func=second_callback)

        managed_function()

        first_callback.assert_called_once()
        second_callback.assert_called_once()
