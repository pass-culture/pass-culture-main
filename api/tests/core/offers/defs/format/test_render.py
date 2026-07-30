from pcapi.core.offers.defs.format import render


class AllSubcategoriesToHtmlTest:
    def test_runs_withtout_any_error(self, tmp_path):
        # ensure that function runs, no need to check for content: it
        # would be too complicated.
        assert render.all_subcategories_to_html(tmp_path / "index.html")
