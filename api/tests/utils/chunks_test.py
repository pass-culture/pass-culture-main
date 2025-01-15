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

    @pytest.mark.parametrize(
        "input_data, chunk_size",
        [
            ([1, 2, 3, 4, 5], 0),
            ([1, 2, 3, 4, 5], -1),
            (range(1, 6), 0),
            (range(1, 6), -1),
        ],
    )
    def test_get_chunks_build_on_empty_chunk_if_chunk_size_is_negative(self, input_data, chunk_size) -> None:
        chunks = list(get_chunks(input_data, chunk_size))
        assert len(chunks) == 0

        for chunk in chunks:
            assert len(chunk) == 0
