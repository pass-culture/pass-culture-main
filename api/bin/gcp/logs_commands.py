#!/usr/bin/env python
import csv
import datetime
import enum
import json
import os
import pprint
import subprocess
import typing

import pydantic as pydantic_v2
import typer
import xlsxwriter
from rich import print
from rich.console import Console
from rich.prompt import Confirm
from rich.prompt import DefaultType
from rich.prompt import InvalidResponse
from rich.prompt import Prompt
from rich.prompt import PromptBase
from rich.prompt import Text
from rich.table import Table
from typing_extensions import Annotated


_CURRENT_CLI_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
_CLI_OUTPUTS_DIRECTORY_NAME = f"{_CURRENT_CLI_DIRECTORY}/outputs"


class _GCPLog(pydantic_v2.BaseModel):
    timestamp: datetime.datetime
    jsonPayload: dict


class InvalidPathException(Exception):
    def __init__(self, path: str):
        super().__init__()
        self.path = path


app = typer.Typer(help="Commands to handle GCP logs file")


class _DumpFormat(enum.StrEnum):
    JSON = "json"
    PYTHON = "python"


class _SpreadsheetFormat(enum.StrEnum):
    XLS = "xls"
    CSV = "csv"


_GroupByOption = Annotated[
    typing.Optional[typing.List[str]],
    typer.Option(help="Group logs by jsonPayload fields (several fields can be given by repeating --group-by option"),
]
_SelectOption = Annotated[
    typing.Optional[typing.List[str]],
    typer.Option(
        help="Select a subsets of jsonPayload fields. You can select several fields can by repeating --select option. You can rename the field in the output by adding `:<new_name>` at the end of the select (for instance: --select 'message:Log message')",
    ),
]
_ScalarOption = Annotated[
    bool,
    typer.Option(help="Get a scalar record instead of dict record (works only if one --select option has been given)"),
]
_DistinctOption = Annotated[bool, typer.Option(help="Return only distinct results (works only with --scalar option)")]
_DumpFormatOption = Annotated[_DumpFormat, typer.Option(help="Dump format (works only with --dump option)")]
_InteractiveOption = Annotated[bool, typer.Option(help="Build the query interactively (other params will be ignored)")]


@app.command()
def query(
    gcp_json_file: Annotated[typer.FileText, typer.Argument(help="Path to the GCP logs JSON")],
    select: _SelectOption = None,
    group_by: _GroupByOption = None,
    scalar: _ScalarOption = False,
    distinct: _DistinctOption = False,
    count: Annotated[bool, typer.Option(help="Count records")] = False,
    dump: Annotated[bool, typer.Option(help="Dump output in outputs folder")] = False,
    dump_format: _DumpFormatOption = _DumpFormat.JSON,
    interactive: _InteractiveOption = False,
) -> None:
    """
    Query a GCP logs file

    We expect the JSON file to look something like this :[{"timestamp": "2025-11-20T12:05:52.555881766Z", "jsonPayload": {"message": "My log message", "extra": {"someObjectId": 23, ...} ...}, ...}]
    """
    if scalar and not select:
        _print_warning("You did not indicate a --select option, --scalar option will be ignore")

    if scalar and select and len(select) > 1:
        _print_warning(
            f"You used the [b]--scalar[/b] option, only the first [b]--select[/b] option ([i]{select[0]}[/i]) will be taken into account"
        )

    gcp_logs = _parse_gcp_logs(gcp_json_file)

    query_options: _InteractiveQueryOptions | None = None
    if interactive:
        available_paths = list(_compute_paths(gcp_logs[0].jsonPayload))
        available_paths.sort()
        query_options = _build_query_interactively(available_paths)

        group_by = query_options.group_by
        select = query_options.select
        dump = query_options.dump
        dump_format = query_options.dump_format
        scalar = query_options.scalar
        count = query_options.count
        distinct = query_options.distinct

    select, aliases = _parse_select(select or [])

    output: list | dict = []
    if group_by:
        output = _get_group_by_result(gcp_logs, group_by=group_by, select=select, scalar=scalar, aliases=aliases)
    else:
        output = [_format_record(gcp_log, select, scalar, aliases) for gcp_log in gcp_logs]

    if scalar and select and distinct:
        output = _return_distinct_records(output)

    if count:
        output = _count_records(output)  # type: ignore[assignment]

    if dump:
        if isinstance(output, int):
            output = {"count": output}

        _make_output_dir_if_missing()

        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = ""

        if dump_format == _DumpFormat.JSON:
            filename = f"{_CLI_OUTPUTS_DIRECTORY_NAME}/{now_str}_output.json"
            _dump_json_file(filename, output)
        else:
            filename = f"{_CLI_OUTPUTS_DIRECTORY_NAME}/{now_str}_output.py"
            _dump_python_file(filename, output)

        _print_success(f"File successfully dumped at [b]{filename}[/b]")
    else:
        print(output)

    if query_options:
        _print_tip("You query corresponds to the following command")
        _print_command_corresponding_to_query_options(gcp_json_file.name, query_options)


@app.command()
def dump_to_spreadsheet(
    gcp_json_file: Annotated[typer.FileText, typer.Argument(help="Path to the GCP logs JSON")],
    select: _SelectOption = None,
    dump: Annotated[bool, typer.Option()] = True,
    dump_format: Annotated[_SpreadsheetFormat, typer.Option()] = _SpreadsheetFormat.XLS,
) -> None:
    """
    Dump GCP logs file into a spreadsheet file

    We expect the JSON file to look something like this :[{"timestamp": "2025-11-20T12:05:52.555881766Z", "jsonPayload": {"message": "My log message", "extra": {"someObjectId": 23, ...} ...}, ...}]
    """

    gcp_logs = _parse_gcp_logs(gcp_json_file)

    headers_aliases: dict = {}

    if select:
        headers = ["timestamp"]
        actual_select, headers_aliases = _parse_select(select)
        headers += actual_select
    else:
        headers = _get_headers_from_gcp_log_json_payload(gcp_logs)

    rows = _format_gcp_logs_to_row_list(headers, gcp_logs, headers_aliases)

    if not dump:
        _print_table_in_terminal(rows)
        return

    _make_output_dir_if_missing()

    now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = ""

    if dump_format == _SpreadsheetFormat.XLS:
        filename = f"{_CLI_OUTPUTS_DIRECTORY_NAME}/{now_str}_output.xlsx"
        _dump_xlsx_workbook(filename=filename, rows=rows)
    elif dump_format == _SpreadsheetFormat.CSV:
        filename = f"{_CLI_OUTPUTS_DIRECTORY_NAME}/{now_str}_output.csv"
        _dump_csv_file(filename=filename, rows=rows)
    _print_success(f"File successfully dumped at [b]{filename}[/b]")


### QUERY helpers


def _parse_gcp_logs(f: typer.FileText) -> list[_GCPLog]:
    """
    Parse the GCP logs file (json file)

    We expect the JSON file to look something like this :[{"timestamp": "2025-11-20T12:05:52.555881766Z", "jsonPayload": {"message": "My log message", "extra": {"someObjectId": 23, ...} ...}, ...}]
    """
    raw_gcp_logs = json.load(f)
    # we reverse the GCP logs because they are ordered by timestamp desc
    return [_GCPLog.model_validate(raw_log) for raw_log in reversed(raw_gcp_logs)]


def _parse_select(select: list[str]) -> tuple[list[str], dict]:
    """
    Return the selected fields list and the fields aliases dict.

    Example:
        >>> fields, aliases = _parse_select(["user_id:Id bénéficiaire", "provider_id:Id du provider", "message"])
        >>> print(fields) # print ["user_id", "provider_id", "message"]
        >>> print(aliases) # print {"user_id": "Id bénéficiaire", "provider_id": "Id du provider"}
    """
    actual_select = []
    headers_aliases = {}

    for selected_field in select:
        if ":" in selected_field:
            field, alias = selected_field.split(":")
            headers_aliases[field] = alias
        else:
            field = selected_field
        actual_select.append(field)

    return actual_select, headers_aliases


def _get_group_by_result(
    gcp_logs: list[_GCPLog],
    *,
    group_by: list[str],
    select: list[str] | None,
    scalar: bool,
    aliases: dict,
) -> dict:
    """
    Return dict where result are grouped by the value contained in the field we want to group by. For instance:

        If your logs file look something like this :
            # the GCP logs file `logs.json`
            [
                {"timestamp": "timestamp1", "jsonPayload": {"message": "log message", "provider_id": 1, "user_id": 23}},
                {"timestamp": "timestamp2", "jsonPayload": {"message": "log message", "provider_id": 2, "user_id": 31}},
                {"timestamp": "timestamp3", "jsonPayload": {"message": "log message", "provider_id": 1, "user_id": 42}},
                {"timestamp": "timestamp4", "jsonPayload": {"message": "log message", "provider_id": 1, "user_id": 23}}
            ]

        The command `python bin/gcp/logs_commands.py query --group-by provider_id` will return
            # the output.json
            {
                1: [
                    {"timestamp": "timestamp1", "jsonPayload": {"message": "log message", "provider_id": 1, "user_id": 23}},
                    {"timestamp": "timestamp3", "jsonPayload": {"message": "log message", "provider_id": 1, "user_id": 42}},
                    {"timestamp": "timestamp4", "jsonPayload": {"message": "log message", "provider_id": 1, "user_id": 23}}
                ],
                2: [
                    {"timestamp": "timestamp2", "jsonPayload": {"message": "log message", "provider_id": 2, "user_id": 31}}
                ]
            }

        You can can chain `--group-by`. For instance `python bin/gcp/logs_commands.py query --group-by provider_id --group-by user_id` will return
            # the output.json
            {
                1: {
                    23: [
                        {"timestamp": "timestamp1", "jsonPayload": {"message": "log message", "provider_id": 1, "user_id": 23}},
                        {"timestamp": "timestamp4", "jsonPayload": {"message": "log message", "provider_id": 1, "user_id": 23}}
                    ],
                    42: [
                        {"timestamp": "timestamp3", "jsonPayload": {"message": "log message", "provider_id": 1, "user_id": 42}}
                    ]

                },
                2: {
                    31: [
                    {"timestamp": "timestamp2", "jsonPayload": {"message": "log message", "provider_id": 2, "user_id": 31}}
                    ]
                }
            }

    """
    result: dict = {}
    for gcp_log in gcp_logs:
        try:
            group_by_values = []
            for path_to_value in group_by:
                nested_value = _get_nested_value(gcp_log.jsonPayload, path_to_value)
                if nested_value == "INVALID_PATH":
                    raise InvalidPathException(path=path_to_value)

                group_by_values.append(nested_value)

            _create_missing_keys(result, group_by_values)
            # thanks to _create_missing_keys we know records is a list
            records: list = _get_nested_value(result, group_by_values)
            record = _format_record(gcp_log=gcp_log, select=select, scalar=scalar, aliases=aliases)
            records.append(record)
        except InvalidPathException as e:
            _print_warning(f"Path [b]`{e.path}`[/b] not found in jsonPayload -> [b]dropping log[/b]")

    return result


def _create_missing_keys(data: dict, path: list[str]) -> dict:
    if len(path) == 1:
        data[path[0]] = data.get(path[0], [])
    else:
        key = path[0]
        next_keys = path[1:]
        data[key] = _create_missing_keys(data.get(key, {}), next_keys)
    return data


def _format_record(gcp_log: _GCPLog, select: list[str] | None, scalar: bool, aliases: dict) -> dict | str | int | None:
    if select is None:
        # Return the "jsonPayload" object enriched with the "timestamp" information
        return dict(timestamp=gcp_log.timestamp.astimezone(datetime.UTC), **gcp_log.jsonPayload)

    if scalar:
        # Return the value contained in jsonPayload[select[0]] (not a dict)
        return _get_nested_value(gcp_log.jsonPayload, select[0])

    formatted_extra_dict = {"timestamp": gcp_log.timestamp.astimezone(datetime.UTC)}
    for path_to_value in select:
        key = aliases.get(path_to_value, path_to_value)
        formatted_extra_dict[key] = _get_nested_value(gcp_log.jsonPayload, path_to_value)

    # Return a dict containing all the selected fields + the timestamp information
    return formatted_extra_dict


def _count_records(output: list | dict) -> dict | int:
    if isinstance(output, list):
        return len(output)

    count_dict = {}
    for key in output.keys():
        count_dict[key] = _count_records(output[key])
    return count_dict


def _return_distinct_records(output: list | dict) -> dict | list:
    if isinstance(output, list):
        return list(set(output))

    distinct_records_dict = {}
    for key in output.keys():
        distinct_records_dict[key] = _return_distinct_records(output[key])
    return distinct_records_dict


### Interactive query helpers


class _InteractiveQueryOptions(pydantic_v2.BaseModel):
    group_by: list[str] | None = None
    select: list[str] | None = None
    dump: bool = False
    dump_format: _DumpFormat = _DumpFormat.JSON
    scalar: bool = False
    count: bool = False
    distinct: bool = False


def _build_query_interactively(available_paths: list[str]) -> _InteractiveQueryOptions:
    query_options = _InteractiveQueryOptions()

    if _confirm("Do you want a scalar result ?"):
        query_options.scalar = True
        select_option = CustomPrompt.ask("Select a key in log", choices=available_paths)
        query_options.select = [select_option]
        if _confirm("Do you want to have distinct results ?"):
            query_options.distinct = True

    query_options.count = _confirm("Do you want to count records ?")

    if not query_options.count and not query_options.scalar:
        if _confirm("Do you want to select a subset of the logs fields ?"):
            query_options.select = ListPrompt.ask(
                "Select the subset of fields (comma-separated)", choices=available_paths
            )
        if query_options.select and _confirm("Do you want to rename some of the field ?"):
            select_with_aliases = []
            for field in query_options.select:
                alias = Prompt.ask(f"Rename field [b]{field}[/b]", default=field)
                if alias != field:
                    field = f"{field}:{alias}"
                select_with_aliases.append(field)
            query_options.select = select_with_aliases

    if _confirm("Do you want to group result by keys ?"):
        query_options.group_by = ListPrompt.ask("Select grouping keys (comma-separated)", choices=available_paths)

    if _confirm("Do you want to dump result ?"):
        query_options.dump = True
        prompted_dump_format = Prompt.ask(
            "Select file format", choices=[_DumpFormat.JSON, _DumpFormat.PYTHON], default=_DumpFormat.JSON
        )
        query_options.dump_format = _DumpFormat.JSON if prompted_dump_format == "json" else _DumpFormat.PYTHON

    return query_options


### Rich Prompt customization


def _long_list_prompt(prompt_instance: PromptBase, default: DefaultType) -> Text:
    prompt = prompt_instance.prompt.copy()
    prompt.end = ""

    if prompt_instance.show_choices and prompt_instance.choices:
        _choices = "\n - ".join(prompt_instance.choices)
        choices = f"[\n - {_choices}\n]"
        prompt.append(" ")
        prompt.append(choices, "prompt.choices")

    if default != ... and prompt_instance.show_default and isinstance(default, (str, prompt_instance.response_type)):
        prompt.append(" ")
        _default = prompt_instance.render_default(default)
        prompt.append(_default)

    prompt.append(prompt_instance.prompt_suffix)

    return prompt


class ListPrompt(PromptBase[list]):
    def process_response(self, value: str) -> list:
        if not value.strip():
            raise InvalidResponse("[red]You must provide at least one item.[/red]")
        result = [v.strip() for v in value.split(",") if v.strip()]
        unknown_choices = set(result) - set(self.choices or [])
        if unknown_choices:
            raise InvalidResponse(f"[red]Some your choices are incorrect: [b]{', '.join(unknown_choices)}[/b][/red]")
        return result

    # overriding parent method (naughty)
    def make_prompt(self, default: DefaultType) -> Text:
        # only way to hack the way choices are displayed
        if self.choices and len(self.choices) > 4:
            return _long_list_prompt(self, default=default)
        return super().make_prompt(default)


class CustomPrompt(Prompt):
    # overriding parent method (naughty)
    def make_prompt(self, default: DefaultType) -> Text:
        # only way to hack the way choices are displayed
        if self.choices and len(self.choices) > 4:
            return _long_list_prompt(self, default=default)
        return super().make_prompt(default)


def _confirm(prompt: str) -> bool:
    return Confirm.ask(prompt, default=False)


### Print utils


def _print_command_corresponding_to_query_options(filename: str, query_options: _InteractiveQueryOptions) -> None:
    """Command print the command corresponding to the options selected in interactive mode"""
    command_lines = [f"python bin/gcp/logs_commands.py [b]query[/b] {filename}"]
    format_option_dict = query_options.model_dump(exclude_unset=True)

    for option in format_option_dict.keys():
        if isinstance(format_option_dict[option], list):
            command_lines += [_to_cli_option(option, value) for value in format_option_dict[option]]
        elif isinstance(format_option_dict[option], str):
            command_lines.append(_to_cli_option(option, format_option_dict[option]))
        elif format_option_dict[option]:
            command_lines.append(_to_cli_option(option))

    _tabulate_print(command_lines)


def _to_cli_option(option_name: str, option_value: str | None = None) -> str:
    cli_option = f"[b]--{option_name.replace('_', '-')}[/b]"
    if option_value:
        cli_option += f" [i]{option_value}[/i]"
    return cli_option


def _tabulate_print(lines: list[str], tab_count: int = 1) -> None:
    tab_unit = "    "
    tab_str = tab_unit * tab_count
    print(tab_str + lines[0], *lines[1:], sep=f" \\\n{tab_str}{tab_unit}")


def _print_success(msg: str) -> None:
    print(f"\n   :white_check_mark: [green][b]Success:[/b] {msg}[/green]\n")


def _print_tip(msg: str) -> None:
    print(f"\n   :bulb: [cyan][b]Info:[/b] {msg}[/cyan]\n")


def _print_warning(msg: str) -> None:
    print(f"\n   :warning: [yellow][b]Warning:[/b] {msg}[/yellow]\n")


def _print_table_in_terminal(rows: list) -> None:
    console = Console()
    table = Table(*rows[0])
    for row_number, row_data in enumerate(rows[1:], start=1):
        table.add_row(*map(str, row_data))
        if row_number > 10:
            _print_warning("We only display the first 10 rows")
            break
    console.print(table)


### Format to row utils


def _format_gcp_logs_to_row_list(headers: list[str], gcp_logs: list[_GCPLog], headers_aliases: dict) -> list:
    header_row = []
    for header in headers:
        header_row.append(headers_aliases.get(header, header))

    rows = [header_row]  # first row contains headers
    for gcp_log in gcp_logs:
        row_data = []
        for header in headers:
            if header == "timestamp":  # only field not in jsonPayload object
                row_data.append(str(gcp_log.timestamp))
                continue

            row_data.append(_get_nested_value(gcp_log.jsonPayload, path_to_value=header))
        rows.append(row_data)
    return rows


def _get_headers_from_gcp_log_json_payload(gcp_logs: list[_GCPLog]) -> list[str]:
    headers = {"timestamp"}  # only field not in jsonPayload object
    for gcp_log in gcp_logs:
        headers |= _compute_paths(gcp_log.jsonPayload)

    ordered_headers_list = list(headers)
    ordered_headers_list.sort()
    return ordered_headers_list


def _compute_paths(json_payload: dict) -> set[str]:
    paths = set()
    for key in json_payload.keys():
        if isinstance(json_payload[key], dict):
            sub_paths = _compute_paths(json_payload[key])
            for sub_path in sub_paths:
                paths.add(f"{key}.{sub_path}")
        else:
            paths.add(key)

    return paths


### Dump utils

_PYTHON_OUTPUT_PATTERN = """
import datetime


output ="""


def _make_output_dir_if_missing() -> None:
    if not os.path.exists(_CLI_OUTPUTS_DIRECTORY_NAME):
        os.mkdir(_CLI_OUTPUTS_DIRECTORY_NAME)


def _dump_json_file(filename: str, output: dict | list) -> None:
    with open(filename, "w", encoding="UTF-8") as f:
        json.dump(output, f, indent=4, sort_keys=True, default=lambda x: str(x))


def _dump_python_file(filename: str, output: dict | list) -> None:
    with open(filename, "w", encoding="UTF-8") as f:
        f.write(_PYTHON_OUTPUT_PATTERN)
        pprint.pprint(output, stream=f)
    subprocess.run(["ruff", "format", filename], check=True)


def _dump_csv_file(filename: str, rows: list) -> None:
    with open(filename, "w+", encoding="utf-8") as fp:
        writer = csv.writer(fp, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        for row in rows:
            writer.writerow(row)


def _dump_xlsx_workbook(filename: str, rows: list) -> None:
    workbook = xlsxwriter.workbook.Workbook(filename=filename)
    worksheet = workbook.add_worksheet("GCP logs")
    for row_number, row_data in enumerate(rows, start=0):
        worksheet.write_row(row_number, 0, data=row_data)
    workbook.close()


# utils functions


def _get_nested_value(nested_dict: dict, path_to_value: list | str) -> typing.Any:
    if isinstance(path_to_value, str):
        path_to_value = path_to_value.split(".")
    current = nested_dict

    for key in path_to_value:
        if not isinstance(current, dict):  # path leads nowhere in nested dict
            current = "INVALID_PATH"
            break
        next = current.get(key, "INVALID_PATH")  # path leads nowhere in nested dict
        current = next

    return current


if __name__ == "__main__":
    app()
