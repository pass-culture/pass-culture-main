import re

from bs4 import BeautifulSoup


def _filter_whitespaces(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def content_as_text(html_content: str) -> str:
    soup = BeautifulSoup(html_content, features="html5lib", from_encoding="utf-8")
    return _filter_whitespaces(soup.text)


def extract_table_rows(html_content: str, parent_id: str | None = None) -> list[dict[str, str]]:
    """
    Extract data from html table (thead + tbody), so that we can compare with expected data when testing routes.
    Every row is a dictionary, in which keys are column headers.
    Note that all data is returned as a string.

    Use `parent_id` parameter to filter inside a html tag id when several tables may be printed in the page.
    """
    soup = BeautifulSoup(html_content, features="html5lib", from_encoding="utf-8")

    if parent_id:
        soup = soup.find(id=parent_id)
        assert soup is not None

    thead = soup.find("thead")
    tbody = soup.find("tbody")
    if thead is None or tbody is None:
        return []

    headers = []
    rows = []

    thead_tr_list = thead.find_all("tr")
    assert len(thead_tr_list) == 1

    for th in thead_tr_list[0].find_all("th"):
        th_text = re.sub(r"\s+", " ", th.text.strip())
        headers.append(th_text)

    # Only main rows, skip additional rows which show more information on click
    tbody_tr_list = tbody.find_all("tr", class_=lambda c: not c or "collapse" not in c)

    for tr in tbody_tr_list:
        row_data = {}
        td_list = tr.find_all(["th", "td"])
        assert len(td_list) == len(headers)
        for idx, td in enumerate(td_list):
            if headers[idx]:
                row_data[headers[idx]] = _filter_whitespaces(td.text)
        rows.append(row_data)

    return rows


def count_table_rows(html_content: str) -> int:
    soup = BeautifulSoup(html_content, features="html5lib", from_encoding="utf-8")

    tbody = soup.find("tbody")
    if tbody is None:
        return 0

    return len(tbody.find_all("tr"))


def extract_pagination_info(html_content: str) -> tuple[int, int, int]:
    """
    Returns current and total pages in pagination block, and total number of results on all pages
    """
    soup = BeautifulSoup(html_content, features="html5lib", from_encoding="utf-8")

    num_results = soup.find("p", class_="num-results")
    if num_results is None:
        total_results = 0
    else:
        m = re.match(r"(\d+) résultat", num_results.text)
        assert m
        total_results = int(m.group(1))

    ul = soup.find("ul", class_="pagination")
    if ul is None:
        return 1, 1, total_results

    page_links = ul.find_all("a", class_="page-link")
    assert page_links
    active_page_link = ul.find("a", class_="page-link active")
    assert active_page_link

    return int(active_page_link.text), len(page_links), total_results


def extract_cards_text(html_content: str) -> list[str]:
    """
    Extract text from all cards in the page, as strings
    """
    soup = BeautifulSoup(html_content, features="html5lib", from_encoding="utf-8")

    cards = soup.find_all("div", class_="card")
    return [_filter_whitespaces(card.text) for card in cards]
