import os
import typing

import sqlalchemy as sa
from flask import Flask
from flask.logging import default_handler
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import orm as sa_orm
from sqlalchemy.event import listens_for
from werkzeug.middleware.profiler import ProfilerMiddleware
from werkzeug.middleware.proxy_fix import ProxyFix

from pcapi import settings
from pcapi.celery_tasks.celery import celery_init_app
from pcapi.celery_tasks.config import CELERY_BASE_SETTINGS
from pcapi.core.finance import utils as finance_utils
from pcapi.models import db
from pcapi.models import install_models
from pcapi.routes import middlewares
from pcapi.utils import jwt
from pcapi.utils.json_encoder import EnumJSONEncoder
from pcapi.utils.logging import install_logging
from pcapi.utils.redis import connect_redis
from pcapi.utils.sentry import init_sentry_sdk


class AppBuilder:
    def before_app_creation(self) -> None:
        """
        install dependancies
        """
        install_logging()
        init_sentry_sdk()
        install_models()

    def create_app(self) -> Flask:
        return Flask("pcapi.flask_app", static_url_path="/static")

    def after_app_creation(self, app: Flask) -> None:
        """Configure flask application"""
        app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_ECHO"] = settings.SQLALCHEMY_ECHO
        app.config["GOOGLE_CLIENT_ID"] = settings.GOOGLE_CLIENT_ID  # for authlib
        app.config["GOOGLE_CLIENT_SECRET"] = settings.GOOGLE_CLIENT_SECRET  # for authlib
        app.config["PROFILE"] = settings.PROFILE_REQUESTS
        app.config.from_mapping(
            CELERY=CELERY_BASE_SETTINGS,
        )
        app.url_map.strict_slashes = False

        # FIXME: move to install_logging ?
        if settings.REMOVE_LOGGER_HANDLER:
            # Remove default logger/handler, since we use our own (see pcapi.core.logging)
            app.logger.removeHandler(default_handler)

        if app.config["PROFILE"]:
            profiling_restrictions = [settings.PROFILE_REQUESTS_LINES_LIMIT]
            # assigning to a method is a type error, but from the docstring of wsgi_app:
            # It's a better idea to do this instead::
            #     app.wsgi_app = MyMiddleware(app.wsgi_app)
            app.wsgi_app = ProfilerMiddleware(  # type: ignore [method-assign]
                app.wsgi_app,
                restrictions=profiling_restrictions,
            )

        # Our GCP L7 load balancer appends 2 IPs to the `X-Forwarded-For` HTTP
        # header: the client IP and the Google Front End IP. Hence `x_for=2`.
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2)  # type: ignore [method-assign]

        app.json_provider_class = EnumJSONEncoder
        app.json = EnumJSONEncoder(app)

    def install_extensions(self, app: Flask) -> None:
        # used in backoffice and discod signin form
        CSRFProtect().init_app(app)
        db.init_app(app)
        sa_orm.configure_mappers()  #  FIXME: move to before_app_creation ?
        celery_init_app(app)

    def install_routes(self, app: Flask) -> None:
        finance_utils.install_template_filters(app)

    def install_handlers(self, app: Flask) -> None:
        from pcapi.routes import error_handlers  # noqa F401

    def install_middleware(self, app: Flask) -> None:
        app.before_request(middlewares.setup_atomic)
        app.before_request(middlewares.setup_sentry_before_request)
        app.after_request(middlewares.log_request_details)
        app.after_request(middlewares.add_security_headers)
        app.after_request(middlewares.mark_4xx_as_invalid)
        app.teardown_request(middlewares.remove_db_session)
        app.teardown_request(middlewares.teardown_atomic)

    def finalize_startup(self, app: Flask) -> None:
        connect_redis()
        jwt.setup_backend(app)

        # FIXME move functions to an other file, just create listeners here
        # Invalidates connections that are being shared accross process boundaries
        # see https://docs.sqlalchemy.org/en/13/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
        @sa.event.listens_for(db.engine, "connect")
        def connect(dbapi_connection: typing.Any, connection_record: typing.Any) -> None:
            connection_record.info["pid"] = os.getpid()

        @sa.event.listens_for(db.engine, "checkout")
        def checkout(dbapi_connection: typing.Any, connection_record: typing.Any, connection_proxy: typing.Any) -> None:
            pid = os.getpid()
            if connection_record.info["pid"] != pid:
                connection_record.connection = connection_proxy.connection = None
                raise sa.exc.DisconnectionError(
                    f"Connection record belongs to pid {connection_record.info['pid']}, attempting to check out in pid {pid}"
                )

        # Install soft deletion hook if enabled
        if settings.SOFTDELETE_ENABLED:

            @listens_for(sa_orm.Session, identifier="do_orm_execute")
            def soft_delete_execute(state: sa_orm.ORMExecuteState) -> None:
                import sqlalchemy_easy_softdelete.handler.rewriter as softdelete_rewriter

                # TODO: check with UPDATE and SELECT in subquery. Does it still work ?
                if not state.is_select:
                    return

                # Rewrite the statement
                global_rewriter = softdelete_rewriter.SoftDeleteQueryRewriter(
                    deleted_field_name="isSoftDeleted",
                    disable_soft_delete_option_name="include_deleted",
                    enabled_tables=[softdelete_rewriter.EnabledTable("venue", None)],
                )
                adapted = global_rewriter.rewrite_statement(state.statement)

                # Replace the statement
                state.statement = adapted
