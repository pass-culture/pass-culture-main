from flask_login import current_user
from flask_login import login_required

from pcapi.connectors.clickhouse import queries as clickhouse_queries
from pcapi.core.offers.repository import venues_have_individual_and_collective_offers
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.statistics_serialize import StatisticsModel
from pcapi.routes.serialization.statistics_serialize import StatisticsQueryModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_venues
from pcapi.utils.transaction_manager import atomic

from . import blueprint
from .venues import aggregate_revenues_by_year


@private_api.route("/get-statistics", methods=["GET"])
@atomic()
@login_required
@spectree_serialize(
    response_model=StatisticsModel, api=blueprint.pro_private_schema, query_params_as_list=["venue_ids"]
)
def get_statistics(query: StatisticsQueryModel) -> StatisticsModel:
    venue_ids = query.venue_ids
    if not venue_ids:
        raise ApiErrors(
            errors={"global": ["Vous devez préciser au moins un ID de partenaire culturel"]},
            status_code=422,
        )
    check_user_has_access_to_venues(current_user, venue_ids)

    results: (
        list[clickhouse_queries.AggregatedCollectiveRevenueModel]
        | list[clickhouse_queries.AggregatedIndividualRevenueModel]
        | list[clickhouse_queries.AggregatedTotalRevenueModel]
    ) = []
    venues_have_individual, venues_have_collective = venues_have_individual_and_collective_offers(venue_ids)
    if not venues_have_individual:
        results = clickhouse_queries.AggregatedCollectiveRevenueQuery().execute({"venue_ids": tuple(venue_ids)})
    elif not venues_have_collective:
        results = clickhouse_queries.AggregatedIndividualRevenueQuery().execute({"venue_ids": tuple(venue_ids)})
    else:
        results = clickhouse_queries.AggregatedTotalRevenueQuery().execute({"venue_ids": tuple(venue_ids)})

    income_by_year = aggregate_revenues_by_year(results)
    return StatisticsModel(income_by_year=income_by_year)
