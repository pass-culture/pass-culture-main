# Copyright 2011 OpenStack Foundation.
# Copyright 2012, Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Exception related utilities.
"""

import functools
import logging
import os
import sys
import time
import traceback

import six


from oslo_utils import encodeutils
from oslo_utils import reflection
from oslo_utils import timeutils


class CausedByException(Exception):
    """Base class for exceptions which have associated causes.

    NOTE(harlowja): in later versions of python we can likely remove the need
    to have a ``cause`` here as PY3+ have implemented :pep:`3134` which
    handles chaining in a much more elegant manner.

    :param message: the exception message, typically some string that is
                    useful for consumers to view when debugging or analyzing
                    failures.
    :param cause: the cause of the exception being raised, when provided this
                  should itself be an exception instance, this is useful for
                  creating a chain of exceptions for versions of python where
                  this is not yet implemented/supported natively.

    .. versionadded:: 2.4
    """
    def __init__(self, message, cause=None):
        super(CausedByException, self).__init__(message)
        self.cause = cause

    def __bytes__(self):
        return self.pformat().encode("utf8")

    def __str__(self):
        return self.pformat()

    def _get_message(self):
        # We must *not* call into the ``__str__`` method as that will
        # reactivate the pformat method, which will end up badly (and doesn't
        # look pretty at all); so be careful...
        return self.args[0]

    def pformat(self, indent=2, indent_text=" ", show_root_class=False):
        """Pretty formats a caused exception + any connected causes."""
        if indent < 0:
            raise ValueError("Provided 'indent' must be greater than"
                             " or equal to zero instead of %s" % indent)
        buf = six.StringIO()
        if show_root_class:
            buf.write(reflection.get_class_name(self, fully_qualified=False))
            buf.write(": ")
        buf.write(self._get_message())
        active_indent = indent
        next_up = self.cause
        seen = []
        while next_up is not None and next_up not in seen:
            seen.append(next_up)
            buf.write(os.linesep)
            if isinstance(next_up, CausedByException):
                buf.write(indent_text * active_indent)
                buf.write(reflection.get_class_name(next_up,
                                                    fully_qualified=False))
                buf.write(": ")
                buf.write(next_up._get_message())
            else:
                lines = traceback.format_exception_only(type(next_up), next_up)
                for i, line in enumerate(lines):
                    buf.write(indent_text * active_indent)
                    if line.endswith("\n"):
                        # We'll add our own newlines on...
                        line = line[0:-1]
                    buf.write(line)
                    if i + 1 != len(lines):
                        buf.write(os.linesep)
                # Don't go deeper into non-caused-by exceptions... as we
                # don't know if there exception 'cause' attributes are even
                # useable objects...
                break
            active_indent += indent
            next_up = getattr(next_up, 'cause', None)
        return buf.getvalue()


def raise_with_cause(exc_cls, message, *args, **kwargs):
    """Helper to raise + chain exceptions (when able) and associate a *cause*.

    NOTE(harlowja): Since in py3.x exceptions can be chained (due to
    :pep:`3134`) we should try to raise the desired exception with the given
    *cause* (or extract a *cause* from the current stack if able) so that the
    exception formats nicely in old and new versions of python. Since py2.x
    does **not** support exception chaining (or formatting) the exception
    class provided should take a ``cause`` keyword argument (which it may
    discard if it wants) to its constructor which can then be
    inspected/retained on py2.x to get *similar* information as would be
    automatically included/obtainable in py3.x.

    :param exc_cls: the exception class to raise (typically one derived
                    from :py:class:`.CausedByException` or equivalent).
    :param message: the text/str message that will be passed to
                    the exceptions constructor as its first positional
                    argument.
    :param args: any additional positional arguments to pass to the
                 exceptions constructor.
    :param kwargs: any additional keyword arguments to pass to the
                   exceptions constructor.

    .. versionadded:: 1.6
    """
    if 'cause' not in kwargs:
        exc_type, exc, exc_tb = sys.exc_info()
        try:
            if exc is not None:
                kwargs['cause'] = exc
        finally:
            # Leave no references around (especially with regards to
            # tracebacks and any variables that it retains internally).
            del(exc_type, exc, exc_tb)
    six.raise_from(exc_cls(message, *args, **kwargs), kwargs.get('cause'))


class save_and_reraise_exception(object):
    """Save current exception, run some code and then re-raise.

    In some cases the exception context can be cleared, resulting in None
    being attempted to be re-raised after an exception handler is run. This
    can happen when eventlet switches greenthreads or when running an
    exception handler, code raises and catches an exception. In both
    cases the exception context will be cleared.

    To work around this, we save the exception state, run handler code, and
    then re-raise the original exception. If another exception occurs, the
    saved exception is logged and the new exception is re-raised.

    In some cases the caller may not want to re-raise the exception, and
    for those circumstances this context provides a reraise flag that
    can be used to suppress the exception.  For example::

      except Exception:
          with save_and_reraise_exception() as ctxt:
              decide_if_need_reraise()
              if not should_be_reraised:
                  ctxt.reraise = False

    If another exception occurs and reraise flag is False,
    the saved exception will not be logged.

    If the caller wants to raise new exception during exception handling
    he/she sets reraise to False initially with an ability to set it back to
    True if needed::

      except Exception:
          with save_and_reraise_exception(reraise=False) as ctxt:
              [if statements to determine whether to raise a new exception]
              # Not raising a new exception, so reraise
              ctxt.reraise = True

    .. versionchanged:: 1.4
       Added *logger* optional parameter.
    """
    def __init__(self, reraise=True, logger=None):
        self.reraise = reraise
        if logger is None:
            logger = logging.getLogger()
        self.logger = logger
        self.type_, self.value, self.tb = (None, None, None)

    def force_reraise(self):
        if self.type_ is None and self.value is None:
            raise RuntimeError("There is no (currently) captured exception"
                               " to force the reraising of")
        six.reraise(self.type_, self.value, self.tb)

    def capture(self, check=True):
        (type_, value, tb) = sys.exc_info()
        if check and type_ is None and value is None:
            raise RuntimeError("There is no active exception to capture")
        self.type_, self.value, self.tb = (type_, value, tb)
        return self

    def __enter__(self):
        # TODO(harlowja): perhaps someday in the future turn check here
        # to true, because that is likely the desired intention, and doing
        # so ensures that people are actually using this correctly.
        return self.capture(check=False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if self.reraise:
                self.logger.error('Original exception being dropped: %s',
                                  traceback.format_exception(self.type_,
                                                             self.value,
                                                             self.tb))
            return False
        if self.reraise:
            self.force_reraise()


def forever_retry_uncaught_exceptions(*args, **kwargs):
    """Decorates provided function with infinite retry behavior.

    The function retry delay is **always** one second unless
    keyword argument ``retry_delay`` is passed that defines a value different
    than 1.0 (less than zero values are automatically changed to be 0.0).

    If repeated exceptions with the same message occur, logging will only
    output/get triggered for those equivalent messages every 60.0
    seconds, this can be altered by keyword argument ``same_log_delay`` to
    be a value different than 60.0 seconds (exceptions that change the
    message are always logged no matter what this delay is set to). As in
    the ``retry_delay`` case if this is less than zero, it will be
    automatically changed to be 0.0.
    """

    def decorator(infunc):
        retry_delay = max(0.0, float(kwargs.get('retry_delay', 1.0)))
        same_log_delay = max(0.0, float(kwargs.get('same_log_delay', 60.0)))

        @six.wraps(infunc)
        def wrapper(*args, **kwargs):
            last_exc_message = None
            same_failure_count = 0
            watch = timeutils.StopWatch(duration=same_log_delay)
            while True:
                try:
                    return infunc(*args, **kwargs)
                except Exception as exc:
                    this_exc_message = encodeutils.exception_to_unicode(exc)
                    if this_exc_message == last_exc_message:
                        same_failure_count += 1
                    else:
                        same_failure_count = 1
                    if this_exc_message != last_exc_message or watch.expired():
                        # The watch has expired or the exception message
                        # changed, so time to log it again...
                        logging.exception(
                            'Unexpected exception occurred %d time(s)... '
                            'retrying.' % same_failure_count)
                        if not watch.has_started():
                            watch.start()
                        else:
                            watch.restart()
                        same_failure_count = 0
                        last_exc_message = this_exc_message
                    time.sleep(retry_delay)
        return wrapper

    # This is needed to handle when the decorator has args or the decorator
    # doesn't have args, python is rather weird here...
    if kwargs or not args:
        return decorator
    else:
        if len(args) == 1:
            return decorator(args[0])
        else:
            return decorator


class exception_filter(object):
    """A context manager that prevents some exceptions from being raised.

    Use this class as a decorator for a function that returns whether a given
    exception should be ignored, in cases where complex logic beyond subclass
    matching is required. e.g.

    >>> @exception_filter
    >>> def ignore_test_assertions(ex):
    ...     return isinstance(ex, AssertionError) and 'test' in str(ex)

    The filter matching function can then be used as a context manager:

    >>> with ignore_test_assertions:
    ...     assert False, 'This is a test'

    or called directly:

    >>> try:
    ...     assert False, 'This is a test'
    ... except Exception as ex:
    ...     ignore_test_assertions(ex)

    Any non-matching exception will be re-raised. When the filter is used as a
    context manager, the traceback for re-raised exceptions is always
    preserved. When the filter is called as a function, the traceback is
    preserved provided that no other exceptions have been raised in the
    intervening time. The context manager method is preferred for this reason
    except in cases where the ignored exception affects control flow.
    """

    def __init__(self, should_ignore_ex):
        self._should_ignore_ex = should_ignore_ex

        if all(hasattr(should_ignore_ex, a)
               for a in functools.WRAPPER_ASSIGNMENTS):
            functools.update_wrapper(self, should_ignore_ex)

    def __get__(self, obj, owner):
        return type(self)(self._should_ignore_ex.__get__(obj, owner))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            return self._should_ignore_ex(exc_val)

    def __call__(self, ex):
        """Re-raise any exception value not being filtered out.

        If the exception was the last to be raised, it will be re-raised with
        its original traceback.
        """
        exc_type, exc_val, traceback = sys.exc_info()

        try:
            if not self._should_ignore_ex(ex):
                if exc_val is ex:
                    six.reraise(exc_type, exc_val, traceback)
                else:
                    raise ex
        finally:
            del exc_type, exc_val, traceback
