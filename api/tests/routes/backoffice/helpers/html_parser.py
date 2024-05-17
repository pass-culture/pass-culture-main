import re

from bs4 import BeautifulSoup


def _filter_whitespaces(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def get_soup(html_content: str, from_encoding: str = "utf-8") -> BeautifulSoup:
    return BeautifulSoup(html_content, features="html5lib", from_encoding=from_encoding)


def content_as_text(html_content: str, from_encoding: str = "utf-8") -> str:
    soup = get_soup(html_content, from_encoding=from_encoding)
    return _filter_whitespaces(soup.text)


def extract_table_rows(html_content: str, parent_class: str | None = None) -> list[dict[str, str]]:
    """
    Extract data from html table (thead + tbody), so that we can compare with expected data when testing routes.
    Every row is a dictionary, in which keys are column headers.
    Note that all data is returned as a string.

    Use `parent_class` parameter to filter inside an html container using a unique class name when several tables may be printed in the page.
    """
    soup = get_soup(html_content)

    if parent_class:
        soup = soup.find(class_=parent_class)
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
    tbody_tr_list = tbody.select("tr:not(.collapse)")

    for tr in tbody_tr_list:
        row_data = {}
        td_list = tr.find_all(["th", "td"])
        assert len(td_list) == len(headers)
        for idx, td in enumerate(td_list):
            if headers[idx]:
                row_data[headers[idx]] = _filter_whitespaces(td.text)
        rows.append(row_data)

    return rows


def count_table_rows(html_content: str, parent_class: str | None = None) -> int:
    soup = get_soup(html_content)

    if parent_class:
        soup = soup.find(class_=parent_class)
        assert soup is not None

    tbody = soup.find("tbody")
    if tbody is None:
        return 0

    return len(tbody.find_all("tr"))


def extract_pagination_info(html_content: str) -> tuple[int, int, int]:
    """
    Returns current and total pages in pagination block, and total number of results on all pages
    """
    soup = get_soup(html_content)

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


def extract(html_content: str, tag: str = "div", class_: str | None = None) -> list[str]:
    """
    Extract text from all <div> matching the class, as strings
    """
    soup = get_soup(html_content)

    if class_ is None:
        elements = soup.find_all(tag)
    else:
        elements = soup.select(f"{tag}.{class_.replace(' ', '.')}")
    return [_filter_whitespaces(element.text) for element in elements]


def extract_cards_text(html_content: str) -> list[str]:
    """
    Extract text from all cards in the page, as strings
    """
    return extract(html_content, class_="card")


def extract_cards_titles(html_content: str) -> list[str]:
    """
    Extract titles from all cards in the page, as strings
    """
    return extract(html_content, tag="h5", class_="card-title")


def extract_alert(html_content: str) -> str:
    """
    Extract the first flash message
    """
    soup = get_soup(html_content)

    alert = soup.find("div", class_="alert")
    assert alert is not None

    return _filter_whitespaces(alert.text)


def get_tag(html_content: str, class_: str, tag: str = "div") -> list[str]:
    """
    Find a tag given its class
    """
    soup = get_soup(html_content)
    tag = soup.find(tag, class_=class_)
    assert tag is not None

    return tag.encode("utf-8")


def extract_alerts(html_content: str) -> str:
    """
    Extract all flash messages
    """
    soup = get_soup(html_content)

    alerts = soup.find_all("div", class_="alert")
    assert alerts

    return [_filter_whitespaces(alert.text) for alert in alerts]


def assert_no_alert(html_content: str) -> str:
    soup = get_soup(html_content)

    alert = soup.find("div", class_="alert")
    assert alert is None


def extract_warnings(html_content: str) -> list[str]:
    # form validation errors have "text-warning" class
    return extract(html_content, tag="p", class_="text-warning")


def extract_select_options(html_content: str, name: str, selected_only: bool = False) -> dict[str, str]:
    soup = get_soup(html_content)

    select = soup.find("select", attrs={"name": name})
    assert select is not None

    options = select.find_all("option", selected=selected_only or None)

    return {option["value"]: _filter_whitespaces(option.text) for option in options if option["value"]}


def extract_input_value(html_content: str, name: str) -> str:
    soup = get_soup(html_content)

    input_field = soup.find("input", attrs={"name": name})
    assert input_field is not None

    return input_field["value"]
