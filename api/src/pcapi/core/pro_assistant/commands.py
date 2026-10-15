import logging

import click

from pcapi.connectors import pro_assistant as pro_assistant_connector
from pcapi.core.pro_assistant import evaluation
from pcapi.core.pro_assistant import knowledge
from pcapi.core.pro_assistant import knowledge_builder
from pcapi.core.pro_assistant import prompt
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("build_pro_assistant_knowledge")
@click.option("--skip-fetch", is_flag=True, default=False, help="Only count tokens of the current knowledge files.")
def build_pro_assistant_knowledge(skip_fetch: bool) -> None:
    """Fetch the public help center articles and measure the size of the assistant prompt.

    The token count uses PRO_ASSISTANT_BACKEND: set it to the Anthropic backend
    (with ANTHROPIC_API_KEY) to get the exact count, the testing backend only estimates it.
    """
    if not skip_fetch:
        articles = knowledge_builder.fetch_help_center_articles()
        knowledge_builder.write_help_center_file(articles)
        click.echo(f"{len(articles)} help center articles written to {knowledge.HELP_CENTER_FILE}")

    system = prompt.build_system_blocks()
    tokens = pro_assistant_connector.count_tokens(
        system=system, messages=[{"role": "user", "content": "Comment créer une offre ?"}]
    )
    click.echo(f"Knowledge base: {len(knowledge.render_knowledge_base())} characters, prompt: {tokens} tokens")
    if not knowledge.NEWS_FILE.exists():
        click.echo(f"Optional Notion news export not found ({knowledge.NEWS_FILE})")


@blueprint.cli.command("run_pro_assistant_eval")
@click.option("--case-id", "case_ids", multiple=True, help="Only run these cases (repeatable).")
def run_pro_assistant_eval(case_ids: tuple[str, ...]) -> None:
    """Ask the evaluation questions to the configured backend and print the scores.

    With the Anthropic backend, this calls the Claude API (a few dollars for the full set).
    """
    cases = [case for case in evaluation.load_cases() if not case_ids or case.id in case_ids]
    results = []
    for case in cases:
        results.append(evaluation.run_case(case))
        click.echo(f"{len(results)}/{len(cases)} {case.id}")
    click.echo(evaluation.format_report(results))
