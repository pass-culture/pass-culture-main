import pytest

from pcapi.utils.csr import get_closest_csr
from pcapi.utils.csr import get_csr


class GetCsrTest:
    @pytest.mark.parametrize(
        "gtl_id",
        ["8040405", "08040405"],
    )
    def test_get_existing_csr(self, gtl_id):
        csr = get_csr(gtl_id)
        assert csr["label"] == "Gestion financière et fiscalité, Bourse"
        assert csr["csr_id"] == "5104"

    @pytest.mark.parametrize(
        "gtl_id",
        ["1919191", "01919191"],
    )
    def test_get_non_existing_csr(self, gtl_id):
        csr = get_csr(gtl_id)

        assert csr is None


class GetClosestCsrTest:
    @pytest.mark.parametrize(
        "gtl_id",
        ["00000000", "0000000"],
    )
    def test_get_non_existing_csr(self, gtl_id):
        csr = get_closest_csr(gtl_id)
        assert csr is None

    @pytest.mark.parametrize(
        "gtl_id,expected_exact_csr,expected_closest_csr",
        (
            ("09080208", None, {"label": "Philosophie Dictionnaires et ouvrages généraux", "csr_id": "4301"}),
            (
                "09080200",
                {"label": "Philosophie Dictionnaires et ouvrages généraux", "csr_id": "4301"},
                {"label": "Philosophie Dictionnaires et ouvrages généraux", "csr_id": "4301"},
            ),
        ),
    )
    def test_get_existing_closest_csr(self, gtl_id, expected_exact_csr, expected_closest_csr):
        exact_csr = get_csr(gtl_id)
        closest_csr = get_closest_csr(gtl_id)
        assert exact_csr == expected_exact_csr
        assert closest_csr == expected_closest_csr
