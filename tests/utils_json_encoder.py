from enum import Enum

import pytest

from utils.json_encoder import EnumJSONEncoder

@pytest.mark.standalone
def test_json_encoder(app):
    class RightsType(Enum):
        admin = "admin"
        editor = "editor"

    obj = {
        'text': "foo",
        'rights': RightsType.editor
    }

    json_string = EnumJSONEncoder().encode(obj)

    assert json_string == '{"text": "foo", "rights": "RightsType.editor"}'
