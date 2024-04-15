import re

import pydantic

from pcapi.utils.clean_accents import clean_accents


DAYS = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")
FR_TO_EN_DAYS = {
    "lundi": "MONDAY",
    "mardi": "TUESDAY",
    "mercredi": "WEDNESDAY",
    "jeudi": "THURSDAY",
    "vendredi": "FRIDAY",
    "samedi": "SATURDAY",
    "dimanche": "SUNDAY",
}
DAYS_OR = "|".join(DAYS)
DAYS_PATTERN = rf"({DAYS_OR})((( )+|de|du|au|a|les|le|et|-|,|:)+({DAYS_OR}))*"
MONTHS = (
    "janvier",
    "fevrier",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "aout",
    "septembre",
    "octobre",
    "novembre",
    "decembre",
)
ANY_DAY = "lundi-dimanche"
WE = "samedi,dimanche"
HOURS_UNITS = "heures|heure|h|:"


class Span(pydantic.BaseModel):
    start: int
    end: int


class SpanDays(Span):
    is_open: bool
    days: list[str]


class SpanHours(Span):
    hours: str


def _normalize(s: str) -> str:
    # Lowercase:
    s = s.lower()

    # Replace en dash with hyphen.
    # Warning! This is done before clean_accents()
    # because clean_accents() removes en dash
    # (e.g.: would break 12h30–13h30 --> 12h3013h30):
    s = s.replace("–", "-")

    # Clean accents:
    s = clean_accents(s)

    # Remove spacing in hours (e.g.: 12 h 30 --> 12h30):
    s = re.sub(rf"(\d{{1,2}})( )+({HOURS_UNITS})( )+(\d{{2}})", r"\g<1>\g<2>\g<3>", s)

    # Normalize days / hours:
    s = re.sub(r"(^|\s+)midi(\s+|$)", " 12h00 ", s)
    s = re.sub(r"(^|\s+)minuit(\s+|$)", " 00h00 ", s)
    s = re.sub(r"(tous les jours|tlj)", f" {ANY_DAY} ", s)
    for pattern in ("week-ends", "week-end", "weekends", "weekend", "we"):
        s = re.sub(rf"(^|\s+){pattern}(\s+|$)", f" {WE} ", s)

    # Remove single dates (e.g.: mardi 22 aout):
    months_str = "|".join(MONTHS)
    s = re.sub(rf"({DAYS_OR})\s+(\d{{1,2}}|1er)\s+({months_str})", "", s)

    # Remove french phone numbers:
    s = re.sub(r"\+?(\d{2})?[. ]*(\d{1,2})?[. ]*\d{2}[. ]*\d{2}[. ]*\d{2}[. ]*\d{2}", "", s)

    return s


# ********
# * Days *
# ********


def _format_days(s: str) -> list[str]:
    s = re.sub(r"(?:^|\s+)(au|a|-)(?:\s+|$)", "-", s)
    s = re.sub(r"(?:^|\s+)(de|du|les|le|et|:)(?:\s+|$)", " , ", s)
    s = s.replace(" ", ",")
    s = re.sub(r"-+", "-", s)
    s = re.sub(r",+", ",", s)
    s = s.strip(",")
    s = s.strip("-")

    days: list[str] = []
    chunks = s.split(",")
    for chunk in chunks:
        if chunk in DAYS:
            days.append(chunk)
            continue
        if "-" not in chunk:
            continue
        splits = chunk.split("-")
        start, end = DAYS.index(splits[0]), DAYS.index(splits[-1]) + 1
        days.extend(DAYS[start:] + DAYS[:end] if start > end else DAYS[start:end])

    return days


def _extract_any_day_but(s: str) -> tuple[str, list[SpanDays]]:
    chunks = []

    # Pattern:
    pattern = rf"(?:{ANY_DAY}).{{1,10}}sauf.{{1,10}}{DAYS_PATTERN}"

    # Matches:
    matches = re.finditer(pattern, s)
    for match in matches:
        start, end = match.span()
        group = match.group()
        days = [day for day in DAYS if day not in _format_days(group.split("sauf")[1])]
        chunk = SpanDays(start=start, end=end, is_open=True, days=days)
        chunks.append(chunk)
        s = s[:start] + "X" * (end - start) + s[end:]

    return s, chunks


def _extract_closed_on(s: str) -> tuple[str, list[SpanDays]]:
    chunks = []

    # Pattern:
    p = r"(?:fermetures|fermeture|fermees|fermee|fermes|ferme)"
    p1 = rf"{DAYS_PATTERN}(?:.{{1,5}}){p}"
    p2 = rf"{p}(?:.{{1,10}}){DAYS_PATTERN}"
    p3 = rf"(?:sauf le|sauf)(?:.{{1,3}}){DAYS_PATTERN}"
    pattern = rf"{p1}|{p2}|{p3}"

    # Matches:
    matches = re.finditer(pattern, s)
    for match in matches:
        start, end = match.span()
        groups = match.groups()
        days = _format_days("".join([g for g in groups if g is not None]))
        chunk = SpanDays(start=start, end=end, is_open=False, days=days)
        chunks.append(chunk)
        s = s[:start] + "X" * (end - start) + s[end:]

    return s, chunks


def _extract_days(s: str) -> tuple[str, list[SpanDays]]:
    chunks = []

    # Pattern:
    pattern = DAYS_PATTERN

    # Matches:
    matches = re.finditer(pattern, s)
    for match in matches:
        start, end = match.span()
        group = match.group()
        days = _format_days(group)
        chunk = SpanDays(start=start, end=end, is_open=True, days=days)
        chunks.append(chunk)
        s = s[:start] + "X" * (end - start) + s[end:]

    return s, chunks


# *********
# * Hours *
# *********


def _extract_hours(s: str) -> tuple[str, list[SpanHours]]:
    chunks = []

    # Pattern:
    p_hours = r"(\d{1,2})"
    p_minutes = r"(\d{0,2})"
    hour_unit = rf"(?:{HOURS_UNITS})"
    p = rf"{p_hours}(?: )*{hour_unit}{p_minutes}"
    sep = r"(?:(?: )+|jusqu'a|et|au|a|-|/)+"
    p1 = rf"{p}{sep}{p}"
    p2 = rf"{p_hours}{sep}{p}"
    p3 = rf"{p}{sep}{p_hours}"
    p4 = rf"{p_hours}{hour_unit}{p_hours}{hour_unit}"
    pattern = rf"{p1}|{p2}|{p3}|{p4}"

    # Matches:
    matches = re.finditer(pattern, s)
    for match in matches:
        start, end = match.span()
        groups = match.groups()
        g_1, g_2, g_3, g_4, g_5, g_6, g_7, g_8, g_9, g_10, g_11, g_12 = groups
        if {g_1, g_2, g_3, g_4} != {None}:
            start_h, start_m, end_h, end_m = g_1, g_2, g_3, g_4
        elif {g_5, g_6, g_7} != {None}:
            start_h, start_m, end_h, end_m = g_5, "00", g_6, g_7
        elif {g_8, g_9, g_10} != {None}:
            start_h, start_m, end_h, end_m = g_8, g_9, g_10, "00"
        elif {g_11, g_12} != {None}:
            start_h, start_m, end_h, end_m = g_11, "00", g_12, "00"
        else:
            raise RuntimeError()
        hours_start = f"{start_h.zfill(2)}:{start_m.zfill(2)}"
        hours_end = f"{end_h.zfill(2)}:{end_m.zfill(2)}"
        chunk = SpanHours(start=start, end=end, hours=hours_start)
        chunks.append(chunk)
        chunk = SpanHours(start=start + 1, end=end, hours=hours_end)
        chunks.append(chunk)
        s = s[:start] + "X" * (end - start) + s[end:]

    return s, chunks


# *****************
# * Opening Hours *
# *****************


def _is_days(group: SpanDays | SpanHours) -> bool:
    return isinstance(group, SpanDays)


def _add_dummy_hours_when_closed(chunks: list[SpanDays | SpanHours]) -> list[SpanDays | SpanHours]:
    new_chunks = []
    for chunk in chunks:
        new_chunks.append(chunk)
        if _is_days(chunk) and not chunk.is_open:  # type: ignore
            new_chunk = SpanHours(start=chunk.start, end=chunk.end, hours="12:00")
            new_chunks.append(new_chunk)
            new_chunk = SpanHours(start=chunk.start, end=chunk.end, hours="12:02")
            new_chunks.append(new_chunk)
    return new_chunks


def _remove_isolated_hours(chunks: list[SpanDays | SpanHours]) -> list[SpanDays | SpanHours]:
    new_chunks = []
    previous_chunk: SpanDays | SpanHours | None = None
    for chunk in chunks:
        if previous_chunk and _is_days(chunk) is _is_days(previous_chunk):
            if not _is_days(chunk) and chunk.start > previous_chunk.start + 20:
                continue
        new_chunks.append(chunk)
        previous_chunk = chunk
    return new_chunks


def _group_chunks(chunks: list[SpanDays | SpanHours]) -> list[list[SpanDays | SpanHours]]:
    new_chunks = []
    cur: list[SpanDays | SpanHours] = []
    for chunk in chunks:
        if not cur:
            cur.append(chunk)
        else:
            if _is_days(cur[-1]) is _is_days(chunk):
                cur.append(chunk)
            else:
                if not _is_days(cur[-1]):
                    if len(cur) < 2:
                        continue
                    if len(cur) % 2 == 1:
                        cur.pop()

                new_chunks.append(cur)
                cur = [chunk]
    if cur:
        new_chunks.append(cur)

    if len(new_chunks) % 2 != 0:
        if _is_days(new_chunks[-1][0]):
            new_chunks.pop()
        else:
            return []

    return new_chunks


def _is_overlapping(hours: list[dict[str, str]], start: str, end: str) -> bool:
    for hour in hours:
        st, ed = hour["open"], hour["close"]
        if st <= start < ed or st < end <= ed:
            return True
    return False


def _get_non_overlapping_hours(chunk_hours: list[SpanHours]) -> list[dict[str, str]]:
    hours: list[dict[str, str]] = []
    for i in range(0, len(chunk_hours), 2):
        start, end = chunk_hours[i].hours, chunk_hours[i + 1].hours
        if not _is_overlapping(hours, start, end):
            hours.append({"open": start, "close": end})
    return hours


def _sanity_checks(opening_hours: dict[str, list[dict[str, str]] | None]) -> None:
    expected_m = ("00", "15", "30", "45", "55")
    en_days = list(FR_TO_EN_DAYS.values())
    for day, hours in opening_hours.items():
        if day not in en_days:
            raise KeyError(day)
        for timespan in hours or []:
            start = timespan["open"]
            start_h, start_m = start.split(":")
            if not (0 <= int(start_h) <= 23) or (start_m not in expected_m):
                raise ValueError(start)

            end = timespan["close"]
            end_h, end_m = end.split(":")
            if not (0 <= int(end_h) <= 23) or (end_m not in expected_m):
                raise ValueError(end)

            if start >= end:
                raise ValueError()


def _get_opening_hours(s: str) -> dict[str, list[dict[str, str]] | None] | None:
    s = _normalize(s)
    s, any_day_but = _extract_any_day_but(s)
    s, closed_on = _extract_closed_on(s)
    s, days = _extract_days(s)
    s, hours = _extract_hours(s)
    chunks = sorted(any_day_but + closed_on + days + hours, key=lambda x: x.start)  # type: ignore
    chunks = _add_dummy_hours_when_closed(chunks)
    chunks = _remove_isolated_hours(chunks)
    chunks = _group_chunks(chunks)  # type: ignore

    opening_hours: dict[str, list | None] = {day: None for day in FR_TO_EN_DAYS.values()}
    for i in range(0, len(chunks), 2):
        if _is_days(chunks[i][0]):  # type: ignore
            chunk_days, chunk_hours = chunks[i], chunks[i + 1]
        else:
            chunk_days, chunk_hours = chunks[i + 1], chunks[i]

        hours = _get_non_overlapping_hours(chunk_hours)  # type: ignore
        for chunk_day in chunk_days:
            for day in chunk_day.days:  # type: ignore
                en_day = FR_TO_EN_DAYS[day]
                if chunk_day.is_open:  # type: ignore
                    opening_hours[en_day] = hours
                else:
                    opening_hours[en_day] = None

    if all(value is None for value in opening_hours.values()):
        return None

    _sanity_checks(opening_hours)

    return opening_hours


def get_opening_hours(s: str) -> dict[str, list[dict[str, str]] | None] | None:
    try:
        opening_hours = _get_opening_hours(s)
    except Exception:  # pylint: disable=broad-exception-caught
        opening_hours = None
    return opening_hours
