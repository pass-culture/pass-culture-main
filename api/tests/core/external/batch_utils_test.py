from pcapi.core.external.batch_utils import batch_length
from pcapi.core.external.batch_utils import shorten_for_batch


def test_batch_length_no_emoji():
    s = "Hello World"
    # Without emojis, batch_length should equal the standard length
    assert batch_length(s) == len(s)


def test_batch_length_with_emoji():
    s = "Hello 😎"
    # "Hello " = 6 characters, "😎" counts as 2, so total should be 8
    assert batch_length(s) == 8


def test_batch_length_multiple_emojis():
    s = "😎😎"
    # Each emoji counts as 2, total should be 4
    assert batch_length(s) == 4


def test_batch_length_complex_emojis():
    # Test with various complex emoji types:
    # - Combined emojis (family, couples)
    # - Skin tone modifiers
    # - Flags
    # - ZWJ sequences (professional emojis)
    # - Directional text emojis
    s = "👨‍👩‍👧‍👦👩🏽‍💻🏳️‍🌈👨🏾‍🦰🫂🇫🇷🤌🦾🧬🎭"
    # Each complex emoji sequence counts differently:
    # 👨‍👩‍👧‍👦 (family) = 8 (4 people joined)
    # 👩🏽‍💻 (woman technologist with medium skin tone) = 4
    # 🏳️‍🌈 (rainbow flag) = 4 (+ 1 for the variation selector)
    # 👨🏾‍🦰 (man with afro and medium-dark skin tone) = 4
    # 🫂 (people hugging) = 2
    # 🇫🇷 (flag) = 4
    # 🤌 (pinched fingers) = 2
    # 🦾 (mechanical arm) = 2
    # 🧬 (dna) = 2
    # 🎭 (performing arts) = 2
    # Total expected length = 35
    assert batch_length(s) == 35


def test_shorten_for_batch_no_truncation():
    s = "Hello World"
    max_length = 20
    # The string is shorter than max_length, so it should be returned unchanged
    assert shorten_for_batch(s, max_length) == s


def test_shorten_for_batch_truncation_no_emoji():
    s = "Hello World, this is a long text"
    max_length = 10
    result = shorten_for_batch(s, max_length)
    # The result should end with the placeholder and not exceed max_length when measured with batch_length
    assert result.endswith("...")
    assert batch_length(result) == max_length


def test_shorten_for_batch_truncation_no_emoji_preserve_words():
    s = "Hello World, this is a long text"
    max_length = 10
    result = shorten_for_batch(s, max_length, preserve_words=True)
    assert result == "Hello..."


def test_shorten_for_batch_truncation_with_emoji():
    s = "Hello 😎, this is a long text with emojis 😎😎"
    max_length = 20
    result = shorten_for_batch(s, max_length)
    # The result should end with the placeholder and its batch length should not exceed max_length
    assert result.endswith("...")
    assert batch_length(result) == max_length


def test_shorten_for_batch_truncation_with_emoji_preserve_words():
    s = "Hello 😎, this is a long text with emojis 😎😎"
    max_length = 25
    result = shorten_for_batch(s, max_length, preserve_words=True)
    assert result == "Hello 😎, this is a..."


def test_shorten_for_batch_exact_boundary():
    # Construct a string where the batch length equals max_length exactly, so no truncation occurs.
    s = "Hello😎"  # "Hello" = 5, "😎" = 2, total = 7
    max_length = 7
    result = shorten_for_batch(s, max_length)
    # Since the string already fits the max_length, it should be returned unchanged.
    assert result == s


def test_shorten_for_batch_complex_emojis():
    s = "👨‍👩‍👧‍👦👩🏽‍💻🏳️‍🌈👨🏾‍🦰🫂🇫🇷🤌🦾🧬🎭"
    # Each complex emoji sequence counts differently:
    # 👨‍👩‍👧‍👦 (family) = 8 (4 people joined)
    # 👩🏽‍💻 (woman technologist with medium skin tone) = 4
    # 🏳️‍🌈 (rainbow flag) = 4
    # 👨🏾‍🦰 (man with afro and medium-dark skin tone) = 4
    # 🫂 (people hugging) = 2
    # 🇫🇷 (flag) = 4
    # 🤌 (pinched fingers) = 2
    # 🦾 (mechanical arm) = 2
    # 🧬 (dna) = 2
    # 🎭 (performing arts) = 2
    max_length = 20
    result = shorten_for_batch(s, max_length, preserve_words=True)
    assert result == "👨‍👩‍👧‍👦👩🏽‍💻🏳️‍🌈..."


def test_shorten_for_batch_variation_selector():
    assert batch_length("🗝️") == 3  # 2 for the keycap and 1 for the variation selector
    s = "🗝️Escape Game à Paris - Entretien avec Gustave Eiffel | Tarif sur le site de l'offre"
    max_length = 64
    result = shorten_for_batch(s, max_length)
    assert result.endswith("...")
    assert result == "🗝️Escape Game à Paris - Entretien avec Gustave Eiffel | Tari..."
    assert batch_length(result) <= max_length
