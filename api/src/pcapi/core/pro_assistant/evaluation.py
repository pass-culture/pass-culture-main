"""Evaluation of the pro assistant on a fixed set of questions.

Run it after every change of the prompt, the knowledge base or the model:
    flask run_pro_assistant_eval
It calls the configured backend (PRO_ASSISTANT_BACKEND): with the Anthropic
backend, it costs a few dollars.
"""

import dataclasses
import json
import pathlib

from pcapi.connectors import pro_assistant as pro_assistant_connector
from pcapi.core.pro_assistant import api
from pcapi.core.pro_assistant import context as context_module
from pcapi.core.pro_assistant import portal_map
from pcapi.core.pro_assistant import prompt
from pcapi.core.pro_assistant import redaction


QUESTIONS_FILE = pathlib.Path(__file__).parent / "evals" / "questions.json"

# Situation of a typical onboarded partner, overridden per case
DEFAULT_CONTEXT = {
    "has_selected_offerer": True,
    "is_validated": True,
    "is_onboarded": True,
    "has_valid_bank_account": True,
}


@dataclasses.dataclass(frozen=True)
class EvalCase:
    id: str
    question: str
    expected_route_ids: list[str] = dataclasses.field(default_factory=list)
    out_of_scope: bool = False
    current_path: str | None = None
    context: dict = dataclasses.field(default_factory=dict)
    forbidden_strings: list[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class EvalResult:
    case: EvalCase
    output: dict | None
    stop_reason: str | None
    route_ok: bool | None  # None when the case does not expect any page
    scope_ok: bool
    leaked_strings: list[str]
    cost_in_microcents: int
    cache_read_input_tokens: int


def load_cases() -> list[EvalCase]:
    return [EvalCase(**raw_case) for raw_case in json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))]


def run_case(case: EvalCase) -> EvalResult:
    assistant_context = context_module.AssistantContext(
        current_route_id=portal_map.find_route_id(case.current_path), **(DEFAULT_CONTEXT | case.context)
    )
    messages = [
        {"role": "user", "content": redaction.redact(case.question)},
        {"role": "system", "content": context_module.render_for_prompt(assistant_context)},
    ]
    sent_payload = json.dumps(messages, ensure_ascii=False)
    result = pro_assistant_connector.generate(
        system=prompt.build_system_blocks(), messages=messages, output_schema=prompt.OUTPUT_SCHEMA
    )

    output = result.output
    returned_route_ids = (output or {}).get("route_ids") or []
    returned_out_of_scope = bool((output or {}).get("out_of_scope"))
    if case.out_of_scope:
        scope_ok = returned_out_of_scope and not returned_route_ids
    else:
        scope_ok = output is not None and not returned_out_of_scope
    route_ok = bool(set(returned_route_ids) & set(case.expected_route_ids)) if case.expected_route_ids else None
    return EvalResult(
        case=case,
        output=output,
        stop_reason=result.stop_reason,
        route_ok=route_ok,
        scope_ok=scope_ok,
        leaked_strings=[string for string in case.forbidden_strings if string in sent_payload],
        cost_in_microcents=api.estimate_cost_in_microcents(result.model, result.usage),
        cache_read_input_tokens=result.usage.cache_read_input_tokens,
    )


def format_report(results: list[EvalResult]) -> str:
    lines = []
    for result in results:
        status = "OK " if result.scope_ok and result.route_ok is not False and not result.leaked_strings else "KO "
        returned = (result.output or {}).get("route_ids") if result.output else f"<{result.stop_reason}>"
        lines.append(
            f"{status} {result.case.id}: pages={returned} hors_sujet={(result.output or {}).get('out_of_scope')}"
        )
    routed = [result for result in results if result.route_ok is not None]
    total_cost_in_cents = sum(result.cost_in_microcents for result in results) / 1_000_000
    cost_per_question_in_cents = total_cost_in_cents / max(len(results), 1)
    lines += [
        "",
        f"Routage : {sum(bool(result.route_ok) for result in routed)}/{len(routed)} bonnes pages proposées",
        f"Périmètre : {sum(result.scope_ok for result in results)}/{len(results)} hors-sujet bien détectés ou évités",
        f"Fuites de données personnelles : {sum(bool(result.leaked_strings) for result in results)}",
        f"Cache : {sum(result.cache_read_input_tokens > 0 for result in results)}/{len(results)} requêtes servies depuis le cache",
        f"Coût : {total_cost_in_cents:.1f} centimes au total, {cost_per_question_in_cents:.2f} centimes par question",
    ]
    return "\n".join(lines)
