import pytest

from pcapi.utils.chunks import get_chunks


class GetChunksTest:
    """
    Ensure that the get_chunks function works properly with a wide
    variety of input types: it must obviously end (meaning it found a
    way to consume properly the input data) and build the expected
    generator
    """

    @pytest.mark.parametrize(
        "input_data",
        [[1, 2, 3, 4, 5], {1, 2, 3, 4, 5}, (x for x in [1, 2, 3, 4, 5]), range(1, 6)],
    )
    def test_get_chunks_with_incomplet_last_chunk(self, input_data) -> None:
        chunks = list(get_chunks(input_data, 2))
        assert chunks == [[1, 2], [3, 4], [5]]

    @pytest.mark.parametrize(
        "input_data",
        [[1, 2, 3, 4, 5], {1, 2, 3, 4, 5}, (x for x in [1, 2, 3, 4, 5]), range(1, 6)],
    )
    def test_get_chunks_with_complet_last_chunk(self, input_data) -> None:
        chunks = list(get_chunks(input_data, 1))
        assert chunks == [[1], [2], [3], [4], [5]]
