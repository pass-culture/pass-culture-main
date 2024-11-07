from flask_login import current_user
from flask_login import login_required

from pcapi.connectors.clickhouse import queries as clickhouse_queries
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization.statistics_serialize import StatisticsModel
from pcapi.routes.serialization.statistics_serialize import StatisticsQueryModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_venues

from . import blueprint


@private_api.route("/get-statistics", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=StatisticsModel, api=blueprint.pro_private_schema, query_params_as_list=["venue_ids"]
)
def get_statistics(query: StatisticsQueryModel) -> StatisticsModel:
    assert isinstance(query.venue_ids, list)
    venue_ids = query.venue_ids
    if not venue_ids:
        raise ApiErrors(
            errors={"global": ["Vous devez préciser au moins un ID de partenaire culturel"]},
            status_code=422,
        )
    check_user_has_access_to_venues(current_user, venue_ids)
    result = clickhouse_queries.YearlyAggregatedRevenueQuery().execute(tuple(venue_ids))
    return StatisticsModel.from_query(income_by_year=result.income_by_year)
