import logging

from pcapi.repository.clean_database import clean_all_database
from pcapi.sandboxes import scripts


logger = logging.getLogger(__name__)


def save_sandbox(name, with_clean=True):  # type: ignore [no-untyped-def]
    if with_clean:
        logger.info("Cleaning database")
        clean_all_database()
        logger.info("All databases cleaned")

    script_name = "sandbox_" + name
    sandbox_module = getattr(scripts, script_name)
    sandbox_module.save_sandbox()
