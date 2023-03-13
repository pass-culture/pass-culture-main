import glob
import os
from pathlib import Path
from subprocess import DEVNULL
from subprocess import Popen
from subprocess import STDOUT

import sass

from pcapi import settings


def preprocess_scss(watch: bool) -> None:
    source = Path("src/pcapi/static/backofficev3/scss")
    destination = Path("src/pcapi/static/backofficev3/css/compiled")
    configuration = Path("src/pcapi/static/backofficev3/scss/boussole.yml")

    Path(destination).mkdir(parents=True, exist_ok=True)

    if settings.IS_RUNNING_TESTS is not True:
        if watch:
            if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
                scss_files = glob.glob(f"{destination}/**/*.css", recursive=True)

                if len(scss_files) == 0:
                    sass.compile(
                        dirname=(source, destination),
                        output_style="compressed",
                        source_map_contents=True,
                        source_map_embed=True,
                        source_map_root=destination,
                    )

                Popen(  # pylint: disable=consider-using-with
                    ["boussole", "watch", "--config", configuration, "--backend", "yaml"],
                    stdout=DEVNULL,
                    stderr=STDOUT,
                )

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
