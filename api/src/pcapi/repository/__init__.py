from contextlib import contextmanager
from dataclasses import dataclass
import functools
import logging
from types import TracebackType
import typing

from flask import g

from pcapi import settings
from pcapi.models import db


logger = logging.getLogger(__name__)


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


@dataclass
class OnCommitCallback:
    func: typing.Callable[[], typing.Any]
    robust: bool

    def __call__(self) -> bool:
        try:
            self.func()
        except Exception as exp:  # pylint: disable=broad-exception-caught
            logger.error(
                "An error was raised in the post commit callbacks",
                extra={
                    "exception": exp,
                    "robust": self.robust,
                },
            )
            return self.robust
        return True


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

        # do not suppress the exception
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
    elif _is_managed_session():
        g._session_to_commit = False


def _mark_session_management() -> None:
    g._session_to_commit = True
    g._managed_session = True
    g._on_commit_callbacks = []


def is_managed_transaction() -> bool:
    """check if we are in a managed transaction block either with `@atomic()` or `with atomic:`"""
    return bool(getattr(g, "_atomic_contexts", False)) or _is_managed_session()


def _is_managed_session() -> bool:
    return getattr(g, "_managed_session", False)


def _manage_session() -> None:
    if not _is_managed_session():
        return
    success = False
    if g._session_to_commit:
        db.session.commit()
        success = True
    else:
        db.session.rollback()

    del g._session_to_commit
    del g._managed_session
    if success:
        on_commit_callbacks = getattr(g, "_on_commit_callbacks", [])
        for callback in on_commit_callbacks:
            if not callback():
                break
    del g._on_commit_callbacks


def on_commit(func: typing.Callable[[], typing.Any], *, robust: bool = False) -> None:
    """
    Hook to execute code after the transaction has been commit. This code will be called outside any
    sql transaction.

    func: a function taking no arguments to call. If your function takes argument you can use the
        function `partial` from `functools` to add the arguments.
    robust: whether or not we should continue to call the other functions after this one failed.

    example
    ```
    from functools import partial
    from pcapi.repository import on_commit

    def function(argument1, argument2):
        ...

    # inside the atomic block:
    on_commit(
        func=partial(function, argument1=1, argument2='foo'),
        robust=False,
    )
    ```
    """
    if not _is_managed_session():
        raise NotImplementedError("on_commit transaction hook is only supported in managed sessions")
    g._on_commit_callbacks.append(OnCommitCallback(func=func, robust=robust))
