import pytest

from .helpers import html_parser


pytestmark = pytest.mark.backoffice


HTML_TABLE_CONTENT = """
<html>
<head>
    <title>Test table</title>
</head>
<body>
<h1>Test table</h1>
<p class="num-results">2 résultats</p>
<table>
    <thead>
        <tr>
            <th>Première colonne</th>
            <th></th>
            <th>Dernière colonne</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>
                12345
            </td>
            <td><button>Valider</button></td>
            <td>
                <a href="/details/12345">
                    Ligne
                    1
                </a>
            </td>
        </tr>
        <tr>
            <td>
                6789
            </td>
            <td><button>Valider</button></td>
            <td>
                <a href="/details/6789">
                    Ligne
                    2
                </a>
            </td>
        </tr>
    </tbody>
</table>
</html>
"""

HTML_PAGINATION_CONTENT = """
<html>
<head>
    <title>Test pagination</title>
</head>
<body>
<h1>Test pagination</h1>
<p class="num-results">32 résultats</p>
<div>...</div>
<div>
    <nav aria-label="Page navigation" class="my-5">
        <ul class="pagination">
            <li class="page-item">
                <a class="page-link" href="/?page=1">1</a>
            </li>
            <li class="page-item">
                <a class="page-link active" href="/?page=2">2</a>
            </li>
            <li class="page-item">
                <a class="page-link" href="/?page=3">3</a>
            </li>
            <li class="page-item">
                <a class="page-link" href="/?page=4">4</a>
            </li>
        </ul>
    </nav>
</div>
</html>
"""


class HtmlParserTest:
    def test_extract_table_rows(self):
        rows = html_parser.extract_table_rows(str.encode(HTML_TABLE_CONTENT))

        assert rows == [
            {"Première colonne": "12345", "Dernière colonne": "Ligne 1"},
            {"Première colonne": "6789", "Dernière colonne": "Ligne 2"},
        ]

    def test_extract_table_rows_no_table(self):
        rows = html_parser.extract_table_rows(str.encode(HTML_PAGINATION_CONTENT))

        assert not rows

    def test_count_table_rows(self):
        count = html_parser.count_table_rows(str.encode(HTML_TABLE_CONTENT))

        assert count == 2

    def test_count_table_rows_no_table(self):
        count = html_parser.count_table_rows(str.encode(HTML_PAGINATION_CONTENT))

        assert count == 0

    def test_extract_pagination_info_single_page(self):
        expected_page, expected_total_pages, total_items = html_parser.extract_pagination_info(
            str.encode(HTML_TABLE_CONTENT)
        )

        assert expected_page == 1
        assert expected_total_pages == 1
        assert total_items == 2

    def test_extract_pagination_info_multiple_pages(self):
        current_page, total_pages, total_items = html_parser.extract_pagination_info(
            str.encode(HTML_PAGINATION_CONTENT)
        )

        assert current_page == 2
        assert total_pages == 4
        assert total_items == 32
