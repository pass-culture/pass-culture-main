from functools import partial
from functools import wraps
from hashlib import sha256
import json
from typing import Any
from typing import Callable
from typing import Iterable
from typing import cast

from flask import current_app
import pydantic


class _CacheProxy:
    def __init__(self, data: str):
        self._json = data
        self._data = None

    def __getattr__(self, name: str) -> Any:
        if self._data is None:
            self._data = json.loads(self._json)
        return self._data.get(name)  # type: ignore [attr-defined]

    def json(self, *args: Iterable[Any], **kwargs: dict[str, Any]) -> str:
        return self._json


def get_from_cache(
    retriever: Callable[..., pydantic.BaseModel | str],
    key_template: str,
    key_args: tuple[str, ...] | dict[str, Any] | None = None,
    expire: int | None = 60 * 60 * 24,  # 24h
    return_type: type = str,
    force_update: bool = False,
) -> pydantic.BaseModel | str:
    """
    Retrieve data from cache if available else use the retriever callable to retrieve data and store it in cache.

    :param key_template: A template to generate the key. This must be compatible with printf style string formatting
        see for documentation: https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
    :param key_args: `list` or `dict` of `str` to fill the template.
    :param retriever: Function to call to retrive the data if they are not in the cache. As it does not take args you
        can use functools.partial to prefill its arguments. It must return a pydantic.BaseModel child or str.
    :param expire: The number of seconds before the cache expires. If None it will be set to never expire.
        It's default value is 86400 (24h).
    :param return_type: Type awaited for return value. This is meant to fool mypy and spectree_serialize and keep
        compatibility. It can be either `BaseModel` or `str`.
    :param force_update: If True force the update of the field cache.
    """
    redis_client = current_app.redis_client  # type: ignore [attr-defined]
    miss = False
    if key_args:
        key = key_template % key_args
    else:
        key = key_template

    data = redis_client.get(key)
    if not data and not redis_client.exists(key):
        miss = True

    if miss or force_update:
        data = retriever()
        if isinstance(data, pydantic.BaseModel):
            data = data.json(exclude_none=False, by_alias=True)
        if expire is not None:
            redis_client.set(key, data.encode("utf-8"), ex=expire)
        else:
            redis_client.set(key, data.encode("utf-8"))

    if return_type is str:
        return data

    return cast(pydantic.BaseModel, _CacheProxy(data=data))


def cached_view(
    *,
    prefix: str = "default",
    expire: int | None = None,
    cache_only_if_no_arguments: bool = True,
    ignore_args: bool = False,
) -> Callable:
    """
    Décorator to cache a view. This decorator MUST be set after spectree_serialize

    By default it only caches the case where no arguments are passed to the view and the cache liftime is set to 24h.

    :param prefix: String to differentiate multiple view with the same name.
    :param expire: The number of seconds before the cache expire. If None it will be set to 24h (default behavior). if
        it is not strictly positive (> 0) the cache will be permanent
    :param cache_only_if_no_arguments: When True only the case when there are no args or kwargs is cached, any other
        case will be a passthrough. Default to True
    :param: ignore_args: If True, the decorator will not look a the args to generate the key and it will always
        considere the args as the default ones. This argument is dangerous, you should not use it.
    """

    def decorator(function: Callable[[Any], pydantic.BaseModel]) -> Callable:
        template = f"api:cached_function:{prefix}:%(func_name)s:args:%(args_hash)s"

        @wraps(function)
        def wrapper(*args: Iterable[Any], **kwargs: dict[str, Any]) -> pydantic.BaseModel:
            if ignore_args:
                args_hash = "args_ignored"
            elif cache_only_if_no_arguments and (args or kwargs):
                return function(*args, **kwargs)
            else:
                args_hash = _compute_arguments_hash(args, kwargs)

            result = get_from_cache(
                key_template=template,
                key_args={"func_name": function.__name__, "args_hash": args_hash},
                retriever=partial(_view_retriever, view=function, args=args, kwargs=kwargs),
                expire=expire,
                return_type=pydantic.BaseModel,
                force_update=False,
            )
            return cast(pydantic.BaseModel, result)

        return wrapper

    return decorator


def _view_retriever(view: Callable[[Any], pydantic.BaseModel], args: Iterable[Any], kwargs: dict[str, Any]) -> str:
    result = view(*args, **kwargs)
    if isinstance(result, pydantic.BaseModel):
        return result.json(exclude_none=False, by_alias=True)
    return result


def _compute_arguments_hash(args: Iterable[Any], kwargs: dict[str, Any]) -> str:
    args_string = ""
    for i, arg in enumerate(args):
        if isinstance(arg, pydantic.BaseModel):
            args_string += f"{i}:{arg.json()}+"
        else:
            args_string += f"{i}:{arg}+"
    for key, arg in kwargs.items():
        if isinstance(arg, pydantic.BaseModel):
            args_string += f"{key}:{arg.json()}+"
        else:
            args_string += f"{key}:{arg}+"
    if args_string:
        # use sha256 to reduce hash collision and cache poisonning
        return sha256(args_string.encode("utf-8")).hexdigest()
    return "default"
