from pcapi.utils.clean_accents import clean_accents


class CleanAccentsTest:
    def test_with_one_accent_word(self):
        accent_word = "école"

        result_word = clean_accents(accent_word)

        assert result_word == "ecole"

    def test_with_many_accents_word(self):
        many_accents_word = "célèbre"

        result_word = clean_accents(many_accents_word)

        assert result_word == "celebre"

    def test_unusual_text(self):
        unusual_text = "Cecï ẽsẗ ůñ téxtë étrẵngè"

        result_text = clean_accents(unusual_text)

        assert result_text == "Ceci est un texte etrange"
