import datetime

from flask_login import current_user
from flask_login import login_required
import sqlalchemy.orm as sqla_orm

import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import finance_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils import human_ids
from pcapi.utils.rest import check_user_has_access_to_offerer


@private_api.route("/finance/<humanized_offerer_id>/invoices", methods=["GET"])
@login_required
@spectree_serialize(response_model=finance_serialize.InvoiceListResponseModel)
def get_invoices(
    humanized_offerer_id: str,
    query: finance_serialize.InvoiceListQueryModel,
) -> finance_serialize.InvoiceListResponseModel:
    offerer_id = human_ids.dehumanize(humanized_offerer_id)
    check_user_has_access_to_offerer(current_user, offerer_id)

    # Frontend sends a period with *inclusive* bounds, but
    # `get_invoices_query` expects the upper bound to be *exclusive*.
    if query.periodEndingDate:
        query.periodEndingDate += datetime.timedelta(days=1)
    invoices = finance_repository.get_invoices_query(
        offerer_id,
        business_unit_id=query.businessUnitId,
        date_from=query.periodBeginningDate,
        date_until=query.periodEndingDate,
    )
    invoices = invoices.options(sqla_orm.joinedload(finance_models.Invoice.businessUnit))
    invoices = invoices.order_by(finance_models.Invoice.date.desc())

    return finance_serialize.InvoiceListResponseModel(
        __root__=[finance_serialize.InvoiceResponseModel.from_orm(invoice) for invoice in invoices],
    )
