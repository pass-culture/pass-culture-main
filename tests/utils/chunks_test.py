import pytest

from pcapi.utils.chunks import get_chunks


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize("items", [(x for x in range(10)), list(range(10))])
def test_get_chunks_from_generator(items):
    """
    Test that the correct number of chunks have been fetched, that each
    one does not exceed the maximum chunk size, and that all of the
    items have been fetched.

    Test that the function returns the same result wether the input is a
    list or a generator.
    """
    chunks = list(get_chunks(3, items))

    assert {len(chunk) for chunk in chunks} == {3, 3, 3, 1}

    expected_ids = set(range(10))
    found_ids = {item for chunk in chunks for item in chunk}
    assert found_ids == expected_ids
