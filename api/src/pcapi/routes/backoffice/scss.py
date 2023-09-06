import glob
import os
from pathlib import Path

import sass

from pcapi import settings


def preprocess_scss(watch: bool) -> None:
    source = Path("src/pcapi/static/backoffice/scss")
    destination = Path("src/pcapi/static/backoffice/css/compiled")
    configuration = Path("src/pcapi/static/backoffice/scss/boussole.yml")

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
                    print("💅 Scss compiler has compiled css 💅", flush=True)
                print(
                    f"💅 watch for scss change with: boussole watch --config {configuration} --backend yaml", flush=True
                )
        else:
            sass.compile(
                dirname=(source, destination),
                output_style="compressed",
                source_map_contents=True,
                source_map_embed=True,
                source_map_root=destination,
            )
            print("💅 Scss compiler has compiled css 💅", flush=True)
