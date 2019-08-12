import inflect

inflect_engine = inflect.engine()


def pluralize(n: int, word: str) -> str:
    return f'{word}s' if n > 1 else word
