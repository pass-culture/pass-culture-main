import pytest

from pcapi.core.offers.exceptions import FileSizeExceeded


class FileSizeExceededTest:
    def test_file_size_exceeded_exception(self):
        exp = FileSizeExceeded(300_000)
        assert str(exp) == "Utilisez une image dont le poids est inférieur à 300.0 kB"

    @pytest.mark.parametrize("data", ((1, "1 Byte"), (3, "3 Bytes"), (2_320_000, "2.3 MB"), (3_992, "4.0 kB")))
    def test_natural_size(self, data):
        result = FileSizeExceeded._natural_size(data[0])
        expected = data[1]
        assert result == expected
