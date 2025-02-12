# isort: off
# This file was automatically generated with `stubgen .../flask/app.py`
# from Flask 2.0.3 and then adapted to our needs. All changes appear
# between `<change>` and `</change>` tags.

import logging
import os
import typing as t
import typing_extensions as te
from . import cli as cli, json as json
from .blueprints import Blueprint as Blueprint
from .config import Config as Config, ConfigAttribute as ConfigAttribute
from .ctx import AppContext as AppContext, RequestContext as RequestContext
from .globals import g as g, session
from .helpers import (
    get_debug_flag as get_debug_flag,
    get_env as get_env,
    get_flashed_messages as get_flashed_messages,
    get_load_dotenv as get_load_dotenv,
    locked_cached_property as locked_cached_property,
    url_for as url_for,
)
from .json import jsonify as jsonify
from .logging import create_logger as create_logger
from .scaffold import Scaffold as Scaffold, find_package as find_package, setupmethod as setupmethod
from .sessions import SecureCookieSessionInterface as SecureCookieSessionInterface
from .signals import (
    appcontext_tearing_down as appcontext_tearing_down,
    got_request_exception as got_request_exception,
    request_finished as request_finished,
    request_started as request_started,
    request_tearing_down as request_tearing_down,
)
from .templating import DispatchingJinjaLoader as DispatchingJinjaLoader, Environment as Environment
from .testing import FlaskCliRunner as FlaskCliRunner, FlaskClient as FlaskClient
from .typing import (
    BeforeFirstRequestCallable as BeforeFirstRequestCallable,
    ErrorHandlerCallable as ErrorHandlerCallable,
    ResponseReturnValue as ResponseReturnValue,
    TeardownCallable as TeardownCallable,
    TemplateFilterCallable as TemplateFilterCallable,
    TemplateGlobalCallable as TemplateGlobalCallable,
    TemplateTestCallable as TemplateTestCallable,
)

from .wrappers import Request as Request, Response as Response
from _typeshed import Incomplete
import redis
from types import TracebackType
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, MapAdapter as MapAdapter, Rule

iscoroutinefunction: Incomplete

# <change>
class GenerateErrorResponse(t.Protocol):
    def __call__(self, errors: dict, backoffice_template_name: str = ...) -> Response:
        pass

# </change>

class Flask(Scaffold):
    request_class = Request
    response_class = Response
    jinja_environment = Environment
    app_ctx_globals_class: Incomplete
    config_class = Config
    testing: Incomplete
    secret_key: Incomplete
    session_cookie_name: Incomplete
    permanent_session_lifetime: Incomplete
    send_file_max_age_default: Incomplete
    use_x_sendfile: Incomplete
    json_encoder: Incomplete
    json_decoder: Incomplete
    jinja_options: dict
    default_config: Incomplete
    url_rule_class = Rule
    url_map_class = Map
    test_client_class: t.Optional[t.Type["FlaskClient"]]
    test_cli_runner_class: t.Optional[t.Type["FlaskCliRunner"]]
    session_interface: Incomplete
    instance_path: Incomplete
    config: Incomplete
    url_build_error_handlers: Incomplete
    before_first_request_funcs: Incomplete
    teardown_appcontext_funcs: Incomplete
    shell_context_processors: Incomplete
    blueprints: Incomplete
    extensions: Incomplete
    url_map: Incomplete
    subdomain_matching: Incomplete
    # <change>
    # Since we set these attributes when building the `app` object,
    # accessing it from many parts of our code causes mypy warnings.
    # So we define them here.
    redis_client: redis.Redis
    generate_error_response: GenerateErrorResponse
    # </change>

    def __init__(
        self,
        import_name: str,
        static_url_path: t.Optional[str] = ...,
        static_folder: t.Optional[t.Union[str, os.PathLike]] = ...,
        static_host: t.Optional[str] = ...,
        host_matching: bool = ...,
        subdomain_matching: bool = ...,
        template_folder: t.Optional[str] = ...,
        instance_path: t.Optional[str] = ...,
        instance_relative_config: bool = ...,
        root_path: t.Optional[str] = ...,
    ) -> None: ...
    # <change>
    # In the real implementation of this class (in Flask), `name` is
    # decorated with `locked_cached_property`. mypy does not like it:
    #     error: Signature of "name" incompatible with supertype "Scaffold"  [override]
    #     note:      Superclass:
    #     note:          str
    #     note:      Subclass:
    #     note:          locked_cached_property
    # When changed into a regular "@property", mypy still complains:
    #     error: Cannot override writeable attribute with read-only property
    # So, let's make it simple and define it as a `str`, like in the
    # parent class.
    name: str
    # </change>
    @property
    def propagate_exceptions(self) -> bool: ...
    @property
    def preserve_context_on_exception(self) -> bool: ...
    # <change>
    # Same as `name` above, `logger` should be a `locked_cached_property`.
    logger: logging.Logger
    # </change>
    # <change>
    # Same as `name` above, `jinja_env` should be a `locked_cached_property`.
    jinja_env: Environment
    # </change>
    @property
    def got_first_request(self) -> bool: ...
    def make_config(self, instance_relative: bool = ...) -> Config: ...
    def auto_find_instance_path(self) -> str: ...
    def open_instance_resource(self, resource: str, mode: str = ...) -> t.IO[t.AnyStr]: ...
    @property
    def templates_auto_reload(self) -> bool: ...
    def create_jinja_environment(self) -> Environment: ...
    def create_global_jinja_loader(self) -> DispatchingJinjaLoader: ...
    def select_jinja_autoescape(self, filename: str) -> bool: ...
    def update_template_context(self, context: dict) -> None: ...
    def make_shell_context(self) -> dict: ...
    env: Incomplete
    @property
    def debug(self) -> bool: ...
    def run(
        self,
        host: t.Optional[str] = ...,
        port: t.Optional[int] = ...,
        debug: t.Optional[bool] = ...,
        load_dotenv: bool = ...,
        **options: t.Any,
    ) -> None: ...
    def test_client(self, use_cookies: bool = ..., **kwargs: t.Any) -> FlaskClient: ...
    def test_cli_runner(self, **kwargs: t.Any) -> FlaskCliRunner: ...
    def register_blueprint(self, blueprint: Blueprint, **options: t.Any) -> None: ...
    def iter_blueprints(self) -> t.ValuesView["Blueprint"]: ...
    def add_url_rule(
        self,
        rule: str,
        endpoint: t.Optional[str] = ...,
        view_func: t.Optional[t.Callable] = ...,
        provide_automatic_options: t.Optional[bool] = ...,
        **options: t.Any,
    ) -> None: ...
    def template_filter(
        self, name: t.Optional[str] = ...
    ) -> t.Callable[[TemplateFilterCallable], TemplateFilterCallable]: ...
    def add_template_filter(self, f: TemplateFilterCallable, name: t.Optional[str] = ...) -> None: ...
    def template_test(
        self, name: t.Optional[str] = ...
    ) -> t.Callable[[TemplateTestCallable], TemplateTestCallable]: ...
    def add_template_test(self, f: TemplateTestCallable, name: t.Optional[str] = ...) -> None: ...
    def template_global(
        self, name: t.Optional[str] = ...
    ) -> t.Callable[[TemplateGlobalCallable], TemplateGlobalCallable]: ...
    def add_template_global(self, f: TemplateGlobalCallable, name: t.Optional[str] = ...) -> None: ...
    def before_first_request(self, f: BeforeFirstRequestCallable) -> BeforeFirstRequestCallable: ...
    def teardown_appcontext(self, f: TeardownCallable) -> TeardownCallable: ...
    def shell_context_processor(self, f: t.Callable) -> t.Callable: ...
    def handle_http_exception(self, e: HTTPException) -> t.Union[HTTPException, ResponseReturnValue]: ...
    def trap_http_exception(self, e: Exception) -> bool: ...
    def handle_user_exception(self, e: Exception) -> t.Union[HTTPException, ResponseReturnValue]: ...
    def handle_exception(self, e: Exception) -> Response: ...
    def log_exception(
        self, exc_info: t.Union[t.Tuple[type, BaseException, TracebackType], t.Tuple[None, None, None]]
    ) -> None: ...
    def raise_routing_exception(self, request: Request) -> te.NoReturn: ...
    def dispatch_request(self) -> ResponseReturnValue: ...
    def full_dispatch_request(self) -> Response: ...
    def finalize_request(
        self, rv: t.Union[ResponseReturnValue, HTTPException], from_error_handler: bool = ...
    ) -> Response: ...
    def try_trigger_before_first_request_functions(self) -> None: ...
    def make_default_options_response(self) -> Response: ...
    def should_ignore_error(self, error: t.Optional[BaseException]) -> bool: ...
    def ensure_sync(self, func: t.Callable) -> t.Callable: ...
    def async_to_sync(self, func: t.Callable[..., t.Coroutine]) -> t.Callable[..., t.Any]: ...
    def make_response(self, rv: ResponseReturnValue) -> Response: ...
    def create_url_adapter(self, request: t.Optional[Request]) -> t.Optional[MapAdapter]: ...
    def inject_url_defaults(self, endpoint: str, values: dict) -> None: ...
    def handle_url_build_error(self, error: Exception, endpoint: str, values: dict) -> str: ...
    def preprocess_request(self) -> t.Optional[ResponseReturnValue]: ...
    def process_response(self, response: Response) -> Response: ...
    def do_teardown_request(self, exc: t.Optional[BaseException] = ...) -> None: ...
    def do_teardown_appcontext(self, exc: t.Optional[BaseException] = ...) -> None: ...
    def app_context(self) -> AppContext: ...
    def request_context(self, environ: dict) -> RequestContext: ...
    def test_request_context(self, *args: t.Any, **kwargs: t.Any) -> RequestContext: ...
    # <change>
    # The `wsgi_app` method has been turned into an attribute so that
    # mypy does not complain when we set it (which is what Flask
    # documentation recommends to set middlewares).
    wsgi_app: t.Callable[[dict, t.Callable], t.Any]
    # </change>
    def __call__(self, environ: dict, start_response: t.Callable) -> t.Any: ...
