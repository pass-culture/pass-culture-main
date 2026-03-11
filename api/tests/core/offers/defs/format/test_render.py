from pcapi.core.offers.defs.format import render


class AllSubcategoriesToHtmlTest:
    def test_runs_withtout_any_error(self, tmp_path):
        assert render.all_subcategories_to_html(tmp_path / "index.html")
