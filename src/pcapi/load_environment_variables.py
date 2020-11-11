import os
from pathlib import Path

from dotenv import load_dotenv

from pcapi.utils.config import ENV
from pcapi.utils.config import IS_DEV


def load_environment_variables() -> None:
    env_path = Path(f"./.env.{ENV}")
    load_dotenv(dotenv_path=env_path)

    if IS_DEV:
        load_dotenv(dotenv_path=".env.local.secret", override=True)
    if os.environ.get("RUN_ENV") == "tests":
        load_dotenv(dotenv_path=".env.testauto", override=True)
