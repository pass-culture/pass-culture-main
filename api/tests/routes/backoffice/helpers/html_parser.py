import re
import typing

from bs4 import BeautifulSoup


sentinel = ...


def _filter_whitespaces(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def get_soup(html_content: str, from_encoding: str = "utf-8") -> BeautifulSoup:
    return BeautifulSoup(html_content, features="html5lib", from_encoding=from_encoding)


def content_as_text(html_content: str, from_encoding: str = "utf-8") -> str:
    soup = get_soup(html_content, from_encoding=from_encoding)
    return _filter_whitespaces(soup.text)


def extract_table_rows(
    html_content: str, parent_class: str | None = None, table_id: str | None = None
) -> list[dict[str, str]]:
    """
    Extract data from html table (thead + tbody), so that we can compare with expected data when testing routes.
    Every row is a dictionary, in which keys are column headers.
    Note that all data is returned as a string.

    Parameters:
    - parent_class: (optional) HTML class name to filter the container that includes the table.
    - table_id: (optional) ID of the table to extract.

    Returns:
    - List of dictionaries representing rows.
    """
    soup = get_soup(html_content)

    if parent_class:
        soup = soup.find(class_=parent_class)
        assert soup is not None, f"Aucun élément avec la classe '{parent_class}' trouvé."

    if table_id:
        table = soup.find("table", id=table_id)
    else:
        table = soup.find("table")

    if table is None:
        return []

    thead = table.find("thead")
    tbody = table.find("tbody")
    if thead is None or tbody is None:
        return []

    headers = []
    rows = []

    thead_tr_list = thead.find_all("tr")
    assert len(thead_tr_list) == 1

    for th in thead_tr_list[0].find_all(["th", "td"]):
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


def count_table_rows(html_content: str, parent_class: str | None = None, table_id: str | None = None) -> int:
    soup = get_soup(html_content)

    if parent_class:
        soup = soup.find(class_=parent_class)
        assert soup is not None

    if table_id:
        table = soup.find("table", id=table_id)
    else:
        table = soup.find("table")

    if table is None:
        return 0

    tbody = table.find("tbody")
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
        m = re.search(r"(\d+)\s+résultat", num_results.text)
        assert m, "no result count found"
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


def extract_alert(html_content: str, raise_if_not_found: bool = True) -> str | None:
    """
    Extract the first flash message
    """
    soup = get_soup(html_content)

    alert = soup.find("div", class_="alert")

    if alert is None and not raise_if_not_found:
        return None

    assert alert is not None
    return _filter_whitespaces(alert.text)


def get_tag(html_content: str, class_: str = sentinel, tag: str = "div", **attrs: typing.Any) -> str:
    """
    Find a tag given its class
    """
    soup = get_soup(html_content)
    if class_ is not sentinel:
        attrs["class_"] = class_
    found_tag = soup.find(tag, **attrs)
    assert found_tag is not None

    return found_tag.encode("utf-8")


def extract_alerts(html_content: str) -> list[str]:
    """
    Extract all flash messages
    """
    soup = get_soup(html_content)

    alerts = soup.find_all("div", class_="alert")
    assert alerts

    return [_filter_whitespaces(alert.text) for alert in alerts]


def assert_no_alert(html_content: str) -> None:
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


def extract_descriptions(html_content: str) -> dict[str, str]:
    description_titles = extract(html_content, tag="dt")
    description_details = extract(html_content, tag="dd")
    assert len(description_titles) == len(description_details)

    return dict(zip(description_titles, description_details))


def extract_badges(html_content: str) -> list[str]:
    return extract(html_content, "span", class_="badge")


def extract_accessibility_badges(html_content: str) -> dict[str, str]:
    soup = get_soup(html_content)

    badge_divs = soup.find_all("figure", class_="accessibility-logo-container")
    badges = {}
    for div in badge_divs:
        badge_soup = get_soup(div.encode("utf-8"))
        badge_caption = badge_soup.find("figcaption")
        assert badge_caption is not None
        badge_text = _filter_whitespaces(badge_caption.text)
        has_ok_icon = badge_soup.find("i", class_="bi-check-circle-fill") is not None
        has_nok_icon = badge_soup.find("i", class_="bi-x-circle-fill") is not None
        assert has_ok_icon != has_nok_icon  # cannot be ok and nok at the same time
        badges[badge_text] = has_ok_icon
    return badges
