import os
from pathlib import Path

import sass

from pcapi import settings


def preprocess_scss() -> None:
    source = Path("src/pcapi/static/backoffice/scss")
    destination = Path("src/pcapi/static/backoffice/css/compiled")
    configuration = Path("src/pcapi/static/backoffice/scss/boussole.yml")

    Path(destination).mkdir(parents=True, exist_ok=True)

    if os.environ.get("WERKZEUG_RUN_MAIN") != "true" and settings.IS_RUNNING_TESTS is not True:
        sass.compile(
            dirname=(source, destination),
            output_style="compressed",
            source_map_contents=True,
            source_map_embed=True,
            source_map_root=destination,
        )
        print("💅 Scss compiler has compiled css 💅", flush=True)
        if settings.IS_DEV:
            print(
                f"💅 Compile scss with: boussole compile --config {configuration} --backend yaml",
                flush=True,
            )
