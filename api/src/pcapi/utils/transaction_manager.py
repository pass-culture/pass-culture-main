import functools
import itertools
import logging
import typing
from dataclasses import dataclass
from traceback import format_exc
from types import TracebackType

import sqlalchemy as sa
from flask import g
from psycopg2 import InternalError as psycopg2_InternalError
from sqlalchemy import exc as sa_exc

from pcapi.models import Model
from pcapi.models import db


logger = logging.getLogger(__name__)


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
        except Exception as exp:
            logger.error(
                "An error was raised in the post commit callbacks",
                extra={
                    "exception": exp,
                    "trace": format_exc(),
                    "robust": self.robust,
                },
            )
            return self.robust
        return True


class atomic:
    """
    This class provides a contextmanager and a decorator to manage the sqlalchemy's session lifecycle.
    It starts by beginning a new session (and a new transaction) and ends with either a commit ( if
    everything is ok) or a rollback (if an exception was not caught or the transaction was marked as
    invalid).

    This class also deactivates autoflush, be sure to flush close to the modification to make debug
    easier.

    While in managed code you should NEVER commit, rollback or begin a session. Instead you can:

    - begin: enter a new atomic managed context. It will create nested session and savepoint in the
        sql session
    - commit: just flush the session, it will commit when exiting the managed code.
    - rollback: use the mark_transaction_as_invalid() function. The session will be rolledback
        instead of being committed

    If you need to do something after the managed code an only if the commit is a success you can
    use on_commit
    """

    def __enter__(self) -> "atomic":
        # In that context g is local to the thread
        # use a list to make the context manager/decorator reentrant

        if _is_managed_session():
            g._atomic_contexts = getattr(g, "_atomic_contexts", [])
            g._atomic_contexts.append(
                AtomicContext(
                    autoflush=db.session.autoflush,
                    invalid_transaction=False,
                )
            )
            db.session.begin_nested()
        else:
            _mark_session_as_managed()
        db.session.autoflush = False
        return self

    def __exit__(
        self,
        exc_type: type | None = None,
        exc_value: Exception | None = None,
        traceback: TracebackType | None = None,
        /,
    ) -> typing.Literal[False]:
        if getattr(g, "_atomic_contexts", []):
            context: AtomicContext = g._atomic_contexts.pop()

            db.session.autoflush = context.autoflush

            if context.invalid_transaction or exc_value is not None:
                db.session.rollback()
            else:
                db.session.commit()

        else:
            db.session.autoflush = True
            # if there is an exception
            if exc_value is not None:
                mark_transaction_as_invalid()
            _finalize_managed_session()
        # do not suppress the exception
        return False

    # decorator part
    def __call__(self, func: typing.Callable) -> typing.Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
            with atomic():
                return func(*args, **kwargs)

        return wrapper


def mark_transaction_as_invalid() -> None:
    """Mark the transaction as to be rolled back by the `atomic_view` decorator or context manager"""
    atomic_contexts = getattr(g, "_atomic_contexts", [])
    if atomic_contexts:
        atomic_contexts[-1].invalid_transaction = True
    elif _is_managed_session():
        g._session_to_commit = False


def _mark_session_as_managed() -> None:
    g._session_to_commit = True
    g._managed_session = True
    g._on_commit_callbacks = []


def is_managed_transaction() -> bool:
    """check if we are in a managed transaction block either with `@atomic()` or `with atomic:`"""
    return bool(getattr(g, "_atomic_contexts", False)) or _is_managed_session()


def _is_managed_session() -> bool:
    return getattr(g, "_managed_session", False)


def _finalize_managed_session() -> None:
    if not _is_managed_session():
        return
    success = False
    if g._session_to_commit:
        db.session.commit()
        success = True
    else:
        db.session.rollback()

    g.pop("_session_to_commit", None)
    g.pop("_managed_session", None)
    if success:
        on_commit_callbacks = getattr(g, "_on_commit_callbacks", [])
        for callback in on_commit_callbacks:
            if not callback():
                break
    g.pop("_on_commit_callbacks", None)

    try:
        db.session.execute(sa.text("SELECT NOW()"))
    except (sa_exc.InternalError, psycopg2_InternalError):
        db.session.rollback()
        raise


def on_commit(func: typing.Callable[[], typing.Any], *, robust: bool = False) -> None:
    """
    Hook to execute code after the transaction has been commit. This code will be called outside any
    sql transaction. If we are not in a managed session it executes the callback immediately.

    func: a function taking no arguments to call. If your function takes argument you can use the
        function `partial` from `functools` to add the arguments.
    robust: whether or not we should continue to call the other functions after this one failed.

    example
    ```
    from functools import partial
    from pcapi.repository.session_management import on_commit

    def function(argument1, argument2):
        ...

    # inside the atomic block:
    on_commit(
        func=partial(function, argument1=1, argument2='foo'),
        robust=False,
    )
    ```
    """
    for args in itertools.chain(getattr(func, "args", []), getattr(func, "keywords", {}).values()):
        if isinstance(args, dict):
            args = args.values()
        elif not isinstance(args, list):
            args = [args]
        for arg in args:
            if isinstance(arg, Model):
                raise ValueError("on_commit cannot be called with a db model")

    if not _is_managed_session():
        func()
    else:
        g._on_commit_callbacks.append(OnCommitCallback(func=func, robust=robust))
