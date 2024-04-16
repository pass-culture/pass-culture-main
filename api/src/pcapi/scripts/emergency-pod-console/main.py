import argparse
import logging
import os
import time


logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()

parser.add_argument("--sleep", type=int, help="Sleep duration in seconds", required=True)


# This is useful for an action to spawn a pod console for a certain duration
# https://github.com/pass-culture/infrastructure/actions/workflows/on_dispatch_pcapi_console_pod.yml
def run_sleep() -> None:
    job_name = os.environ.get("JOB_NAME")
    args = parser.parse_args()
    logger.info("emergency-pod-console:sleep(%s):%s:start", args.sleep, job_name)
    time.sleep(args.sleep)
    logger.info("emergency-pod-console:sleep(%s):%s:end", args.sleep, job_name)


run_sleep()
