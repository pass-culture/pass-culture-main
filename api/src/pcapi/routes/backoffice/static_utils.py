from collections import namedtuple
from contextlib import suppress
import hashlib
import os
from pathlib import Path

import sass

from pcapi import settings


HashesContainer = namedtuple("HashesContainer", ("js", "css"))
hashes = HashesContainer("", "")


JS_BUNDLE = Path("src/pcapi/static/backoffice/js/bundle.js")
JS_FILES = [
    # Hotwired turbo frame,
    Path("src/pcapi/static/backoffice/js/libs/@hotwired/turbo@v8.0.12/dist/turbo.es2017-umd.js"),
    # Bootstrap JS,
    Path("src/pcapi/static/backoffice/js/libs/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"),
    Path("src/pcapi/static/backoffice/js/libs/tom-select@2.4.1/dist/js/tom-select.complete.min.js"),
    # Vanilla datetime range picker
    Path("src/pcapi/static/backoffice/js/libs/momentjs@2.30.1/moment.min.js"),
    Path(
        "src/pcapi/static/backoffice/js/libs/vanilla-datetimerange-picker@latest/dist/vanilla-datetimerange-picker.js"
    ),
    # Our core libs,
    Path("src/pcapi/static/backoffice/js/core/pc-utils.js"),
    Path("src/pcapi/static/backoffice/js/core/pc-event-handler.js"),
    Path("src/pcapi/static/backoffice/js/core/pc-addon.js"),
    # Our app,
    Path("src/pcapi/static/backoffice/js/core/pc-backoffice-app.js"),
    # Our JS libs,
    Path("src/pcapi/static/backoffice/js/addons/bs-tooltips.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-validation-filters.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-forms-check-validity.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-tom-select-field.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-override-custom-textarea-enter.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-table-multi-select.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-batch-action-form.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-postal-address-autocomplete.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-registration-steps.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-filter-dataset.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-confirm-modal.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-reset-modal-turbo-src.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-field-list.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-form-field.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-clipboard.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-date-range-field.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-form.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-pro-search-form.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-strip-query-string.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-hide-on-click.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-display-selector.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-table-manager.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-submit-form-button.js"),
    Path("src/pcapi/static/backoffice/js/addons/pc-section-focus-onload.js"),
]
CSS_BUNDLE = Path("src/pcapi/static/backoffice/css/bundle.css")
CSS_FILES = [
    # Tom Select JS configuration
    Path("src/pcapi/static/backoffice/css/tom-select@2.4.1/dist/css/tom-select.css"),
    Path("src/pcapi/static/backoffice/css/tom-select-bootstrap-5.min.css"),
    # Vanilla datetime range picker
    Path("src/pcapi/static/backoffice/css/vanilla-datetimerange-picker@latest/dist/vanilla-datetimerange-picker.css"),
    # Our css needs to be imported after Bootstrap to have a stronger weight
    Path("src/pcapi/static/backoffice/css/compiled/pc/pc.css"),
]


def generate_bundles() -> None:
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true" and settings.IS_RUNNING_TESTS is not True:
        preprocess_scss()
        print("💅auto rebuild bundles by settings ENABLE_BO_BUNDLES_AUTORELOAD to 1", flush=True)
        generate_bundle(JS_FILES, JS_BUNDLE)
        generate_bundle(CSS_FILES, CSS_BUNDLE)


def preprocess_scss() -> None:
    source = Path("src/pcapi/static/backoffice/scss")
    destination = Path("src/pcapi/static/backoffice/css/compiled")
    configuration = Path("src/pcapi/static/backoffice/scss/boussole.yml")

    Path(destination).mkdir(parents=True, exist_ok=True)

    sass.compile(
        dirname=(source, destination),
        output_style="compressed",
        source_map_contents=True,
        source_map_embed=True,
        source_map_root=destination,
    )
    print(f"💅compile scss with: boussole compile --config {configuration} --backend yaml", flush=True)


def get_hashes() -> HashesContainer:
    global hashes  # pylint: disable=global-statement  # noqa: PLW0603 (global-statement)
    if settings.ENABLE_BO_BUNDLES_AUTORELOAD:
        # make it easier to debug js and css files in bo (but it takes a few ms for each http call)
        generate_bundle(JS_FILES, JS_BUNDLE)
        generate_bundle(CSS_FILES, CSS_BUNDLE)
    if settings.ENABLE_BO_BUNDLES_AUTORELOAD or not hashes.js:
        with suppress(FileNotFoundError):
            js = _retrieve_hash(JS_BUNDLE)
            css = _retrieve_hash(CSS_BUNDLE)
            hashes = HashesContainer(js=js, css=css)
    return hashes


def _retrieve_hash(file_path: Path) -> str:
    with open(file_path, mode="r", encoding="utf-8") as fp:
        data = fp.read(66)
        return data[2:]


def generate_bundle(files: list[Path], destination: Path) -> None:
    with suppress(FileNotFoundError):
        os.unlink(destination)

    bundle_content = b""
    for filepath in files:
        bundle_content += f"/* {filepath} */\n".encode("utf-8")
        with open(filepath, mode="rb") as fp:
            bundle_content += fp.read()
            bundle_content += b"\n"

    bundle_hash = hashlib.sha256(bundle_content).hexdigest()
    bundle_content = (f"/*{bundle_hash}*/\n").encode("utf-8") + bundle_content

    with open(destination, mode="wb") as fp:
        fp.write(bundle_content)
