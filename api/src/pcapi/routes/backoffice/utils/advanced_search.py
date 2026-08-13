import datetime
import enum
import operator as op
import typing
from collections import defaultdict

import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects import postgresql

from pcapi.models import db
from pcapi.utils import date as date_utils


OPERATOR_DICT: dict[str, dict[str, typing.Any]] = {
    "EQUALS": {"function": op.eq},
    "IS": {"function": op.eq},
    "NOT_EQUALS": {"function": op.ne},
    "NAME_EQUALS": {"function": lambda x, y: x.ilike(y)},
    "NAME_NOT_EQUALS": {"function": lambda x, y: ~x.ilike(y)},
    "GREATER_THAN": {"function": op.gt},
    "GREATER_THAN_OR_EQUAL_TO": {"function": op.ge},
    "LESS_THAN": {"function": op.lt},
    "LESS_THAN_OR_EQUAL_TO": {"function": op.le},
    "DATE_FROM": {"function": lambda x, y: x >= date_utils.date_to_localized_datetime(y, datetime.time.min)},
    "DATE_TO": {"function": lambda x, y: x <= date_utils.date_to_localized_datetime(y, datetime.time.max)},
    "DATE_EQUALS": {
        "function": lambda x, y: x.between(
            date_utils.date_to_localized_datetime(y, datetime.time.min),
            date_utils.date_to_localized_datetime(y, datetime.time.max),
        )
    },
    "IN": {"function": lambda x, y: x.in_(y)},
    "NULLABLE": {"function": lambda x, y: x.is_(None) if y else x.is_not(None)},
    "NOT_IN": {"function": lambda x, y: x.not_in(y)},
    "CONTAINS": {"function": lambda x, y: x.ilike(f"%{y}%")},
    "NO_CONTAINS": {"function": lambda x, y: ~x.ilike(f"%{y}%")},
    "NOT_EXIST": {"function": lambda x, y: x.is_(None), "outer_join": True},
    "INTERSECTS": {"function": lambda x, y: x.overlap(postgresql.array(obj for obj in y))},
    "NOT_INTERSECTS": {"function": lambda x, y: ~x.overlap(postgresql.array(obj for obj in y))},
}


ALGOLIA_OPERATOR_DICT: dict[str, typing.Any] = {
    "IN": lambda x, y: ([f"{x}:{i}" for i in y],),
    "NOT_IN": lambda x, y: ([f"{x}:-{i}" for i in y], False, True),
    "EQUALS": lambda x, y: (f"{x}:{y}",),
    "NOT_EQUALS": lambda x, y: (f"{x}:-{y}",),
    "NUMBER_EQUALS": lambda x, y: (f"{x}={y}", True),
    "GREATER_THAN_OR_EQUAL_TO": lambda x, y: (f"{x}>={y}", True),
    "LESS_THAN": lambda x, y: (f"{x}<{y}", True),
    "DATE_FROM": lambda x, y: (
        f"{x}>={round(date_utils.date_to_localized_datetime(y, datetime.time.min).timestamp())}",  # type: ignore [union-attr]
        True,
    ),
    "DATE_TO": lambda x, y: (
        f"{x}<={round(date_utils.date_to_localized_datetime(y, datetime.time.max).timestamp())}",  # type: ignore [union-attr]
        True,
    ),
    "DATE_EQUALS": lambda x, y: (
        [ALGOLIA_OPERATOR_DICT["DATE_FROM"](x, y)[0], ALGOLIA_OPERATOR_DICT["DATE_TO"](x, y)[0]],
        True,
        True,
    ),
}

LLM_OPERATOR_DICT: dict[str, str] = {
    "IN": "in",
    "NOT_IN": "in",
    "EQUALS": "=",
    "GREATER_THAN": ">",
    "GREATER_THAN_OR_EQUAL_TO": ">=",
    "LESS_THAN": "<",
    "LESS_THAN_OR_EQUAL_TO": "=<",
}


class AdvancedSearchOperators(enum.Enum):
    EQUALS = "est égal à"
    NOT_EQUALS = "est différent de"
    NAME_EQUALS = "est égal à\0"  # the \0 is here to force wtforms to display EQUALS and NAME_EQUALS
    NAME_NOT_EQUALS = "est différent de\0"  # the \0 is here to force wtforms to display NOT_EQUALS and NAME_NOT_EQUALS
    NUMBER_EQUALS = "égal"
    GREATER_THAN = "supérieur strict"
    GREATER_THAN_OR_EQUAL_TO = "supérieur ou égal"
    LESS_THAN = "inférieur strict"
    LESS_THAN_OR_EQUAL_TO = "inférieur ou égal"
    DATE_FROM = "à partir du"
    DATE_TO = "jusqu'au"
    DATE_EQUALS = "est exactement le"
    IN = "est parmi"
    NOT_IN = "n'est pas parmi"
    NULLABLE = "est"
    CONTAINS = "contient"
    NO_CONTAINS = "ne contient pas"
    NOT_EXIST = "n'a aucun"
    INTERSECTS = "contient\0"  # the \0 is here to force wtforms to display CONTAINS and INTERSECTS
    NOT_INTERSECTS = "ne contient pas\0"  # the \0 is here to force wtforms to display NO_CONTAINS and NOT_INTERSECTS


def generate_search_query(
    query: sa_orm.Query,
    *,
    search_parameters: typing.Iterable[dict[str, typing.Any]],
    fields_definition: dict[str, dict[str, typing.Any]],
    joins_definition: dict[str, list[dict[str, typing.Any]]],
    subqueries_definition: dict[str, dict[str, typing.Any]],
    _ignore_subquery_joins: bool = False,
) -> tuple[sa_orm.Query, set[str], set[str], set[str]]:
    """
    Generate a search query from a list of dict (from a ListField of FormFields).

    query: the query object to use
    search_parameters: list of dict representing the user's query. each dict must have at least the fields:
        - operator: a key for operators_definition
        - search_field: a key for fields_definition
    fields_definition: a dict defining the fields, inner_joins and special operations
    joins_definition: a dict defining how to do each join
    subqueries_definition: a dict defining how to do each subquery (hack to avoid a slower distinct)
    operators_definition: a dict mapping str to actual operations
    _ignore_subquery_joins: internal signaling to manage subqueries
    """
    subquery_joins: dict = defaultdict(list)
    inner_joins: set[str] = set()
    outer_joins: set[str] = set()
    filters: list = []
    warnings: set[str] = set()
    for search_data in search_parameters:
        operator = search_data.get("operator", "")
        if operator not in OPERATOR_DICT:
            continue

        search_field = search_data.get("search_field")
        if not search_field:
            continue

        meta_field = fields_definition.get(search_field)
        if not meta_field:
            warnings.add(f"La règle de recherche '{search_field}' n'est pas supportée, merci de prévenir les devs")
            continue

        if "subquery_join" in meta_field and not _ignore_subquery_joins:
            subquery_joins[meta_field["subquery_join"]].append(search_data)
            continue

        field_value = meta_field.get("special", lambda x: x)(search_data.get(meta_field["field"]))

        if custom_filter := meta_field.get("custom_filters", {}).get(operator):
            filters.append(custom_filter(field_value))
            if custom_filter_inner_joins := meta_field.get("custom_filters_inner_joins", {}).get(operator, set()):
                inner_joins.update(custom_filter_inner_joins)
            continue

        if query_modifier := meta_field.get("query_modifier", {}).get("function"):
            filter_value = field_value

            # query_modifier should take as arguments the base query and the filter values
            # if the operator is NOT_IN, the filter values should be all the possible values except the selected ones
            if operator == "NOT_IN":
                choices = meta_field["query_modifier"]["choices"]
                filter_value = set(choices) - set(filter_value)

            query = query_modifier(query, filter_value)
            continue
        column = meta_field["column"]
        if OPERATOR_DICT[operator].get("outer_join", False):
            if not meta_field.get("outer_join") or not meta_field.get("outer_join_column"):
                warnings.add(
                    f"La règle de recherche '{search_field}' n'est pas correctement configurée pour "
                    f"l'opérateur '{operator}', merci de prévenir les devs"
                )
                continue
            outer_joins.add(meta_field["outer_join"])
            column = meta_field["outer_join_column"]
        elif "inner_join" in meta_field:
            inner_joins.add(meta_field["inner_join"])
        filters.append(OPERATOR_DICT[operator]["function"](column, field_value))

    query, inner_join_log = _manage_joins(query=query, joins=inner_joins, joins_definition=joins_definition)
    query, outer_join_log = _manage_joins(
        query=query, joins=outer_joins, joins_definition=joins_definition, join_type="outer_join"
    )
    filters.extend(
        _manage_subquery_joins(
            joins=subquery_joins,
            fields_definition=fields_definition,
            subqueries_definition=subqueries_definition,
        )
    )
    if filters:
        query = query.filter(*filters)
    return query, inner_join_log, outer_join_log, warnings


def _manage_joins(
    query: sa_orm.Query,
    joins: set,
    joins_definition: dict[str, list[dict[str, typing.Any]]],
    join_type: str = "inner_join",
) -> tuple[sa_orm.Query, set[str]]:
    join_log = set()
    join_containers = sorted((joins_definition[join] for join in joins), key=len, reverse=True)
    for join_container in join_containers:
        for join_dict in join_container:
            if join_dict["name"] not in join_log:
                if join_type == "inner_join":
                    query = query.join(*join_dict["args"])
                elif join_type == "outer_join":
                    query = query.outerjoin(*join_dict["args"])
                else:
                    raise ValueError(f"Unsupported join_type {join_type}. Supported : 'inner_join' or 'outer_join'.")
                join_log.add(join_dict["name"])
    return query, join_log


def _manage_subquery_joins(
    joins: dict,
    fields_definition: dict[str, dict[str, typing.Any]],
    subqueries_definition: dict[str, dict[str, typing.Any]],
) -> list:
    filters = []
    for join_name, subquery_filters in joins.items():
        subquery = db.session.query(subqueries_definition[join_name]["table"])
        subquery, *_ = generate_search_query(
            query=subquery,
            search_parameters=subquery_filters,
            fields_definition=fields_definition,
            joins_definition={},
            subqueries_definition={},
            _ignore_subquery_joins=True,
        )
        subquery = subquery.filter(subqueries_definition[join_name]["constraint"])
        filters.append(subquery.limit(1).exists())
    return filters


def generate_algolia_search_string(
    search_parameters: typing.Iterable[dict[str, typing.Any]],
    fields_definition: dict[str, dict[str, typing.Any]],
) -> tuple[dict, set[str]]:
    filter_dict: dict[str, list[list[str] | str]] = {
        "facetFilters": [],
        "numericFilters": [],
    }
    warnings: set[str] = set()
    for search_data in search_parameters:
        operator = search_data.get("operator", "")
        if operator not in ALGOLIA_OPERATOR_DICT:
            continue
        search_field = search_data.get("search_field")
        if not search_field:
            continue

        meta_field = fields_definition.get(search_field)
        if not meta_field:
            warnings.add(f"La règle de recherche '{search_field}' n'est pas supportée, merci de prévenir les devs")
            continue
        field_value = meta_field.get("algolia_special", lambda x: x)(search_data.get(meta_field["field"]))

        result, *options = ALGOLIA_OPERATOR_DICT[operator](meta_field["facet"], field_value)
        is_number = options[0] if len(options) else False
        is_and_operator = options[1] if len(options) >= 2 else False

        if not is_and_operator:
            result = [result]

        if is_number:
            filter_dict["numericFilters"].extend(result)
        else:
            filter_dict["facetFilters"].extend(result)

    return filter_dict, warnings


def generate_llm_search_dict(
    search_parameters: typing.Iterable[dict[str, typing.Any]],
    fields_definition: dict[str, dict[str, typing.Any]],
) -> tuple[list, set[str]]:
    filters = []
    warnings: set[str] = set()
    for search_data in search_parameters:
        operator = search_data.get("operator", "")
        if operator not in LLM_OPERATOR_DICT:
            continue

        search_field = search_data.get("search_field")
        if not search_field:
            continue

        meta_field = fields_definition.get(search_field)
        if not meta_field:
            warnings.add(f"La règle de recherche '{search_field}' n'est pas supportée, merci de prévenir les devs")
            continue
        field_value = meta_field.get("llm_special", lambda x: x)(search_data.get(meta_field["field"]))
        operator_string = LLM_OPERATOR_DICT[operator]
        field_name = meta_field["llm_filter"]
        filters.append(
            {
                "column": field_name,
                "operator": operator_string,
                "value": field_value,
            }
        )

    return filters, warnings
