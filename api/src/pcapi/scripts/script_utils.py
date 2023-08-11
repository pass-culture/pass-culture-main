import datetime
import os
import socket
import statistics

import pytz


HOSTNAME = socket.gethostname()


def get_eta(end, current, elapsed_per_batch, batch_size: int):  # type: ignore [no-untyped-def]
    left_to_do = end - current
    eta = left_to_do / batch_size * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta


def _get_remote_to_local_cmd(file_path: str, env: str) -> str:
    return f"kubectl cp -n {env} {HOSTNAME}:{file_path} {os.path.basename(file_path)}"


def log_remote_to_local_cmd(output_files: list[str]) -> None:
    env = ""
    if "staging" in HOSTNAME:
        env = "staging"
    elif "production" in HOSTNAME:
        env = "production"

    if env:
        download_file_cmds = "\n            ".join(
            [_get_remote_to_local_cmd(output_file, env) for output_file in output_files]
        )
        print(
            f"""
        To download output files:

        {download_file_cmds}

        """
        )
