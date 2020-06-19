import os
from dotenv import load_dotenv
from pathlib import Path

def load_environment_configuration_variables():
    env_file = '.env.' + os.getenv('ENV')
    env_path = Path('.') / env_file
    load_dotenv(dotenv_path=env_path)
