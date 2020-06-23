import os
from dotenv import load_dotenv
from pathlib import Path

from utils.config import IS_DEV


def load_environment_variables():
    env_path = Path(f'./.env.{os.environ.get("ENV")}')
    load_dotenv(dotenv_path=env_path)

    if IS_DEV:
        load_dotenv(dotenv_path='.env.local.secret')
