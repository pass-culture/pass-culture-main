from pcapi.utils.custom_logic import OPERATIONS


def test_soft_equal_return_true():
    a = 2
    b = 2
    result = OPERATIONS["=="](a, b)
    assert result


def test_soft_equal_return_false():
    a = 2
    b = 3
    result = OPERATIONS["=="](a, b)
    assert not result


def test_not_soft_equal_return_true():
    a = 2
    b = 2
    result = OPERATIONS["!="](a, b)
    assert not result


def test_not_soft_equal_return_false():
    a = 2
    b = 3
    result = OPERATIONS["!="](a, b)
    assert result


def test_greater_than_return_false():
    a = 2
    b = 3
    result = OPERATIONS[">"](a, b)
    assert not result


def test_greater_than_return_true():
    a = 3
    b = 2
    result = OPERATIONS[">"](a, b)
    assert result


def test_greater_or_equal_than_return_false():
    a = 2
    b = 3
    result = OPERATIONS[">="](a, b)
    assert not result


def test_greater_or_equal_than_return_true():
    a = 3
    b = 3
    result = OPERATIONS[">="](a, b)
    assert result


def test_greater_or_equal_than_return_true_when_a_is_greater():
    a = 4
    b = 3
    result = OPERATIONS[">="](a, b)
    assert result


def test_less_than_return_false():
    a = 3
    b = 2
    result = OPERATIONS["<"](a, b)
    assert not result


def test_less_than_return_true():
    a = 2
    b = 3
    result = OPERATIONS["<"](a, b)
    assert result


def test_less_or_equal_than_return_false():
    a = 3
    b = 2
    result = OPERATIONS["<="](a, b)
    assert not result


def test_less_or_equal_than_return_true():
    a = 3
    b = 3
    result = OPERATIONS["<="](a, b)
    assert result


def test_less_or_equal_than_return_true_when_a_is_less():
    a = 3
    b = 4
    result = OPERATIONS["<="](a, b)
    assert result


def test_in_return_true():
    a = "hello"
    b = ["hello", "World"]
    result = OPERATIONS["in"](a, b)
    assert result


def test_in_return_false():
    a = "hello"
    b = ["Goodbye", "City"]
    result = OPERATIONS["in"](a, b)
    assert not result


def test_not_in_return_true():
    a = "hello"
    b = ["Goodbye", "City"]
    result = OPERATIONS["not in"](a, b)
    assert result


def test_not_in_return_false():
    a = "hello"
    b = ["hello", "Goodbye"]
    result = OPERATIONS["not in"](a, b)
    assert not result


def test_contains_return_true():
    a = "A suspicious offer"
    b = ["hello", "suspicious"]
    result = OPERATIONS["contains"](a, b)
    assert result


def test_contains_return_false():
    a = "A suspicious offer"
    b = ["hello", "world"]
    result = OPERATIONS["contains"](a, b)
    assert not result


def test_equals_word_with_accents():
    a = "l'école est fermée"
    b = "l'ècole est fermee"
    result = OPERATIONS["=="](a, b)
    assert result


def test_contains_with_words_with_accents():
    a = "je ne vais plus à l'écÔle"
    b = ["ecole", "marche"]
    result = OPERATIONS["contains"](a, b)
    assert result


def test_in_with_words_with_accents():
    a = "dérèglement"
    b = ["le", "dérèglement", "climatique"]
    result = OPERATIONS["in"](a, b)
    assert result
