from contextlib import contextmanager
from dataclasses import dataclass
import functools
from types import TracebackType
import typing

from flask import g

from pcapi import settings
from pcapi.models import db


# FIXME: cue for queries count in tests to remove when all routes will be atomics
if settings.IS_RUNNING_TESTS:
    _test_is_session_managed: bool = False


# DEPRECATED in favor of @atomic() because @transaction() is not reentrant
@contextmanager
def transaction() -> typing.Iterator[None]:
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


@dataclass
class AtomicContext:
    autoflush: bool
    invalid_transaction: bool


class atomic:
    def __enter__(self) -> "atomic":
        # In that context g is local to the thread
        # use a list to make the context manager/decorator reentrant
        g._atomic_contexts = getattr(g, "_atomic_contexts", [])
        g._atomic_contexts.append(
            AtomicContext(
                autoflush=db.session.autoflush,
                invalid_transaction=False,
            )
        )
        db.session.begin_nested()
        db.session.autoflush = False
        return self

    def __exit__(
        self,
        exc_type: type | None = None,
        exc_value: Exception | None = None,
        traceback: TracebackType | None = None,
        /,
    ) -> typing.Literal[False]:
        context: AtomicContext = g._atomic_contexts.pop()

        db.session.autoflush = context.autoflush

        if context.invalid_transaction or exc_value is not None:
            db.session.rollback()
        else:
            db.session.commit()

        # do not supress the exception
        return False

    # decorator part
    def __call__(self, func: typing.Callable) -> typing.Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore [no-untyped-def]
            if _is_managed_session():
                # use the context manager part to make the decorator reeantrant.
                with type(self):
                    return func(*args, **kwargs)
            else:
                _mark_session_management()
                with db.session.no_autoflush:
                    try:
                        return func(*args, **kwargs)
                    except Exception as exp:
                        mark_transaction_as_invalid()
                        raise exp
                    finally:
                        _manage_session()

        return wrapper


def mark_transaction_as_invalid() -> None:
    """Mark the transaction as to be rolled back by the `atomic_view` decorator or context manager"""
    atomic_contexts = getattr(g, "_atomic_contexts", [])
    if atomic_contexts:
        atomic_contexts[-1].invalid_transaction = True
    else:
        if _is_managed_session():
            g._session_to_commit = False


def _mark_session_management() -> None:
    g._session_to_commit = True
    g._managed_session = True
    if settings.IS_RUNNING_TESTS:
        global _test_is_session_managed  # pylint: disable=global-statement
        _test_is_session_managed = True


def _is_managed_session() -> bool:
    return getattr(g, "_managed_session", False)


def _manage_session() -> None:
    if _is_managed_session():
        if g._session_to_commit:
            db.session.commit()
        else:
            db.session.rollback()

        del g._session_to_commit
        del g._managed_session


def _test_helper_get_is_session_managed() -> bool:
    if settings.IS_RUNNING_TESTS:
        return _test_is_session_managed
    raise RuntimeError("This global variable is only available for test purpose")


def _test_helper_reset_is_session_managed() -> None:
    if settings.IS_RUNNING_TESTS:
        global _test_is_session_managed  # pylint: disable=global-statement
        _test_is_session_managed = False
    else:
        raise RuntimeError("This global variable is only available for test purpose")
