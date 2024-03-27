import logging
import os
import argparse

from pcapi import settings

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()

# Optional argument
parser.add_argument("--opt_arg", type=int, help="An optional integer argument")

parser.add_argument("--switch", action="store_true", help="A boolean switch", default=False)


def run_this_script() -> None:
    args = parser.parse_args()
    print("Argument values:")
    print(args.switch)
    print(args.opt_arg)
    print(f"test display settings.ENABLE_COMMAND_CLEAN_DATABASE:{settings.ENABLE_COMMAND_CLEAN_DATABASE}")
    logger.info("test:pcapi-console-job")
    f = open(f"{os.environ.get('OUTPUT_DIRECTORY')}/hello_python_world.txt", "w")
    f.write("hello python!")
    f.close()


run_this_script()
