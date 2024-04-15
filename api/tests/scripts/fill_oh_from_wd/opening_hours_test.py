import textwrap

from pcapi.scripts.fill_oh_from_wd.opening_hours import get_opening_hours


class OpeningHoursTest:
    def test_1(self):
        s = "Ouvert du lundi au vendredi de 9h à 12h et de 14h à 18h"
        opening_hours = get_opening_hours(s)
        assert opening_hours == {
            "MONDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}],
            "TUESDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}],
            "WEDNESDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}],
            "THURSDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}],
            "FRIDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}],
            "SATURDAY": None,
            "SUNDAY": None,
        }

    def test_2(self):
        s = "Tous les jours de 10h00 à 19h00."
        opening_hours = get_opening_hours(s)
        assert opening_hours == {
            "MONDAY": [{"open": "10:00", "close": "19:00"}],
            "TUESDAY": [{"open": "10:00", "close": "19:00"}],
            "WEDNESDAY": [{"open": "10:00", "close": "19:00"}],
            "THURSDAY": [{"open": "10:00", "close": "19:00"}],
            "FRIDAY": [{"open": "10:00", "close": "19:00"}],
            "SATURDAY": [{"open": "10:00", "close": "19:00"}],
            "SUNDAY": [{"open": "10:00", "close": "19:00"}],
        }

    def test_3(self):
        s = "mardi 14h00-19h00 mercredi au dimanche 10h00-14h00 et 16h00-19h00"
        opening_hours = get_opening_hours(s)
        assert opening_hours == {
            "MONDAY": None,
            "TUESDAY": [{"open": "14:00", "close": "19:00"}],
            "WEDNESDAY": [{"open": "10:00", "close": "14:00"}, {"open": "16:00", "close": "19:00"}],
            "THURSDAY": [{"open": "10:00", "close": "14:00"}, {"open": "16:00", "close": "19:00"}],
            "FRIDAY": [{"open": "10:00", "close": "14:00"}, {"open": "16:00", "close": "19:00"}],
            "SATURDAY": [{"open": "10:00", "close": "14:00"}, {"open": "16:00", "close": "19:00"}],
            "SUNDAY": [{"open": "10:00", "close": "14:00"}, {"open": "16:00", "close": "19:00"}],
        }

    def test_4(self):
        s = "Horaires d'ouverture : du lundi au samedi : 13h30 - 22h45 Dimanche 10h30 - 22h45"
        opening_hours = get_opening_hours(s)
        assert opening_hours == {
            "MONDAY": [{"open": "13:30", "close": "22:45"}],
            "TUESDAY": [{"open": "13:30", "close": "22:45"}],
            "WEDNESDAY": [{"open": "13:30", "close": "22:45"}],
            "THURSDAY": [{"open": "13:30", "close": "22:45"}],
            "FRIDAY": [{"open": "13:30", "close": "22:45"}],
            "SATURDAY": [{"open": "13:30", "close": "22:45"}],
            "SUNDAY": [{"open": "10:30", "close": "22:45"}],
        }

    def test_5(self):
        s = "Horaires d'ouverture : les mardi et jeudi de 14h00 à 19h00, les mercredi et vendredi de 9h00 à 12h00 et de 14h00 à 19h00 et le samedi de 14h00 à 17h00."
        opening_hours = get_opening_hours(s)
        assert opening_hours == {
            "MONDAY": None,
            "TUESDAY": [{"open": "14:00", "close": "19:00"}],
            "WEDNESDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "19:00"}],
            "THURSDAY": [{"open": "14:00", "close": "19:00"}],
            "FRIDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "19:00"}],
            "SATURDAY": [{"open": "14:00", "close": "17:00"}],
            "SUNDAY": None,
        }

    def test_6(self):
        s = """\
        Les réservations peuvent être retirées Le mardi et le  samedi de 10h à 19h.
        Le mercredi, le jeudi et le vendredi de 13H à 19h.
        """
        s = textwrap.dedent(s)
        opening_hours = get_opening_hours(s)
        assert opening_hours == {
            "MONDAY": None,
            "TUESDAY": [{"open": "10:00", "close": "19:00"}],
            "WEDNESDAY": [{"open": "13:00", "close": "19:00"}],
            "THURSDAY": [{"open": "13:00", "close": "19:00"}],
            "FRIDAY": [{"open": "13:00", "close": "19:00"}],
            "SATURDAY": [{"open": "10:00", "close": "19:00"}],
            "SUNDAY": None,
        }
