import pathlib


def _read_stopwords_file(filename: str):
    path = pathlib.Path(__file__).parent / filename
    words = {line.strip() for line in path.read_text().splitlines() if not line.startswith("#")}
    return words - {""}


STOPWORDS = _read_stopwords_file("stopwords.txt")
