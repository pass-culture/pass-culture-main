import glob
import os
from pathlib import Path
import signal
from subprocess import DEVNULL
from subprocess import Popen
from subprocess import STDOUT

import sass

from pcapi import settings


def preprocess_scss(watch: bool) -> None:
    source = Path("src/pcapi/static/backofficev3/scss")
    destination = Path("src/pcapi/static/backofficev3/css/compiled")
    configuration = Path("src/pcapi/static/backofficev3/scss/boussole.yml")
    pid_file_path = Path("src/pcapi/static/backofficev3/scss/boussole.pid")

    Path(destination).mkdir(parents=True, exist_ok=True)

    if settings.IS_RUNNING_TESTS is not True:
        if watch:
            if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
                has_never_compiled_css = len(glob.glob(f"{destination}/**/*.css", recursive=True)) == 0
                if has_never_compiled_css:
                    sass.compile(
                        dirname=(source, destination),
                        output_style="compressed",
                        source_map_contents=True,
                        source_map_embed=True,
                        source_map_root=destination,
                    )

                # kill previous boussole process if python previously crashed
                try:
                    if os.path.isfile(pid_file_path):
                        with open(pid_file_path, "r", encoding="utf8") as pid_file:
                            pid = int(pid_file.read())
                            pid_file.close()
                            os.kill(pid, signal.SIGTERM)
                except Exception:  # pylint: disable=broad-except
                    pass

                proc = Popen(  # pylint: disable=consider-using-with
                    ["boussole", "watch", "--config", configuration, "--backend", "yaml"],
                    stdout=DEVNULL,
                    stderr=STDOUT,
                )

                # save new process pid in case of python crash
                with open(pid_file_path, "w", encoding="utf8") as pid_file:
                    pid_file.write(str(proc.pid))
                    pid_file.close()

                print("💅 Scss compiler attached and watching, enjoy styling 💅", flush=True)
        else:
            sass.compile(
                dirname=(source, destination),
                output_style="compressed",
                source_map_contents=True,
                source_map_embed=True,
                source_map_root=destination,
            )
            print("💅 Scss compiler has compiled css 💅", flush=True)
