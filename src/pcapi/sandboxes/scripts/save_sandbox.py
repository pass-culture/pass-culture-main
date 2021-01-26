from pcapi.repository.clean_database import clean_all_database
from pcapi.sandboxes import scripts
from pcapi.utils.logger import logger


def save_sandbox(name, with_clean=True):
    if with_clean:
        logger.info("Cleaning all databases 🧽")
        clean_all_database()
        logger.info("All databases cleaned ✅")

    script_name = "sandbox_" + name
    sandbox_module = getattr(scripts, script_name)
    sandbox_module.save_sandbox()
