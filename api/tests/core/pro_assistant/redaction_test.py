import pytest

from pcapi.core.pro_assistant import redaction


class RedactTest:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Mon email est jean.dupont+pc@exemple.fr merci", "Mon email est [EMAIL] merci"),
            ("Mon IBAN FR76 3000 6000 0112 3456 7890 189 est refusé", "Mon IBAN [IBAN] est refusé"),
            ("IBAN FR7630006000011234567890189", "IBAN [IBAN]"),
            ("SIRET 123 456 789 00012", "SIRET [SIRET]"),
            ("SIRET 12345678900012", "SIRET [SIRET]"),
            ("SIREN 123456789", "SIREN [SIREN]"),
            ("Appelez le 06 12 34 56 78", "Appelez le [TELEPHONE]"),
            ("Appelez le +33 6 12 34 56 78", "Appelez le [TELEPHONE]"),
            ("Appelez le 01.23.45.67.89", "Appelez le [TELEPHONE]"),
            ("La contremarque AZE123 est invalide", "La contremarque [CONTREMARQUE] est invalide"),
            ("Carte 4970 1012 3456 7890", "Carte [CARTE]"),
            ("Voir https://exemple.fr/compte?token=abc", "Voir [URL]"),
        ],
    )
    def test_personal_data_is_redacted(self, text, expected):
        assert redaction.redact(text) == expected

    @pytest.mark.parametrize(
        "text",
        [
            "Comment créer une offre collective ADAGE en 2026 pour 30 élèves ?",
            "Le code postal 75001 et un prix de 12,50 €",
            "Je veux créer une OFFRE pour mon CINEMA",
        ],
    )
    def test_regular_questions_are_untouched(self, text):
        assert redaction.redact(text) == text
