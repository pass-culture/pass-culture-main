import datetime
import enum
import operator
import os
import pathlib
import uuid

from pcapi.core.offerers import factories as offerers_factories


def json_default(data):
    conversions = {
        enum.Enum: operator.attrgetter("value"),
        datetime.datetime: str,
        uuid.UUID: str,
    }
    for type_, func in conversions.items():
        if isinstance(data, type_):
            return func(data)

    return data


def gen_offerer_tags():
    tags = [offerers_factories.OffererTagFactory(label=label) for label in ("Collectivité", "Établissement public")]
    tags.append(offerers_factories.OffererTagFactory(name="partenaire-national", label="Partenaire national"))
    return tags


def run_command(app, command_name, *args):
    runner = app.test_cli_runner()
    args = (command_name, *args)
    return runner.invoke(args=args)


class StorageFolderManager:
    storage_folder: pathlib.Path

    def teardown_method(self) -> None:
        """clear extracts after each tests"""
        try:
            for child in self.storage_folder.iterdir():
                if not child.is_file():
                    continue
                child.unlink()
        except FileNotFoundError:
            pass

    def setup_method(self):
        """Create the folder to work with"""
        os.makedirs(self.storage_folder, exist_ok=True)
