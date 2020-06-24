import os
from dotenv import load_dotenv
from pathlib import Path

from utils.config import IS_DEV, ENV


def load_environment_variables():
    env_path = Path(f'./.env.{ENV}')
    load_dotenv(dotenv_path=env_path)

    if IS_DEV:
        load_dotenv(dotenv_path='.env.local.secret')
