import os
from dotenv import load_dotenv
from pathlib import Path

def load_environment_configuration_variables():
    env_path = Path(f'./.env.{os.environ.get("ENV")}')
    load_dotenv(dotenv_path=env_path)
