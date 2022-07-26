import datetime

from flask_login import current_user
from flask_login import login_required
import sqlalchemy.orm as sqla_orm

import pcapi.core.finance.api as finance_api
import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.repository as finance_repository
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import finance_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.rest import check_user_has_access_to_offerer

from . import blueprint


@private_api.route("/finance/invoices", methods=["GET"])
@login_required
@spectree_serialize(response_model=finance_serialize.InvoiceListResponseModel, api=blueprint.pro_private_schema)
def get_invoices(
    query: finance_serialize.InvoiceListQueryModel,
) -> finance_serialize.InvoiceListResponseModel:
    # Frontend sends a period with *inclusive* bounds, but
    # `get_invoices_query` expects the upper bound to be *exclusive*.
    if query.periodEndingDate:
        query.periodEndingDate += datetime.timedelta(days=1)
    invoices = finance_repository.get_invoices_query(
        current_user,
        business_unit_id=query.businessUnitId,
        reimbursement_point_id=query.reimbursementPointId,
        date_from=query.periodBeginningDate,
        date_until=query.periodEndingDate,
    )
    invoices = invoices.options(sqla_orm.joinedload(finance_models.Invoice.businessUnit))
    invoices = invoices.options(
        sqla_orm.joinedload(finance_models.Invoice.cashflows).joinedload(finance_models.Cashflow.batch)
    )
    invoices = invoices.order_by(finance_models.Invoice.date.desc())

    return finance_serialize.InvoiceListResponseModel(
        __root__=[finance_serialize.InvoiceResponseModel.from_orm(invoice) for invoice in invoices],
    )


@private_api.route("/finance/business-units", methods=["GET"])
@login_required
@spectree_serialize(response_model=finance_serialize.BusinessUnitListResponseModel, api=blueprint.pro_private_schema)
def get_business_units(query: finance_serialize.BusinessUnitListQueryModel) -> None:
    if query.offerer_id:
        check_user_has_access_to_offerer(current_user, query.offerer_id)
    business_units = finance_repository.get_business_units_query(
        user=current_user,
        offerer_id=query.offerer_id,
    )
    business_units = business_units.options(
        sqla_orm.contains_eager(finance_models.BusinessUnit.bankAccount),
    )
    business_units = business_units.order_by(finance_models.BusinessUnit.name)
    return finance_serialize.BusinessUnitListResponseModel(  # type: ignore [return-value]
        __root__=[
            finance_serialize.BusinessUnitResponseModel.from_orm(business_unit) for business_unit in business_units
        ],
    )


@private_api.route("/finance/business-units/<int:business_unit_id>", methods=["PATCH"])
@login_required
@spectree_serialize(on_success_status=204, api=blueprint.pro_private_schema)
def edit_business_unit(business_unit_id: int, body: finance_serialize.BusinessUnitEditionBodyModel) -> None:
    business_unit = finance_models.BusinessUnit.query.filter_by(id=business_unit_id).first_or_404()
    if business_unit.siret:
        msg = "Ce point de facturation a déjà un SIRET, vous ne pouvez pas le modifier."
        raise ApiErrors({"siret": [msg]})
    venue = business_unit.venues[0]
    check_user_has_access_to_offerer(current_user, venue.managingOffererId)
    try:
        finance_api.edit_business_unit(business_unit, siret=body.siret)
    except finance_exceptions.InvalidSiret:
        raise ApiErrors({"siret": ["Ce SIRET n'est pas valide."]})
