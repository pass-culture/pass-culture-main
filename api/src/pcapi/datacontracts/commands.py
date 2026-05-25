import logging

from open_data_contract_standard.model import OpenDataContractStandard
from open_data_contract_standard.model import SchemaObject
from open_data_contract_standard.model import SchemaProperty

from pcapi.core.offers.models import Offer
from pcapi.models import Model as PCAPIModel
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


# Create a custom class that implements import_source method
def _get_datacontract_standard() -> OpenDataContractStandard:
    open_data_contract = OpenDataContractStandard(
        id="1",
        name="Datacontract pcapi DB",
        version="O.O.1",
    )
    open_data_contract.schema_ = []
    sqla_models: list[type[PCAPIModel]] = [Offer]

    for model in sqla_models:
        columns_schemas = []
        for column in model.__table__.columns:
            columns_schemas.append(SchemaProperty(name=column.name, physicalType=str(column.type)))

        open_data_contract.schema_.append(SchemaObject(name=model.__tablename__, properties=columns_schemas))

    return open_data_contract


@blueprint.cli.command("generate_datacontract")
def generate_datacontract() -> None:
    data_contract_standard = _get_datacontract_standard()
    print(data_contract_standard.to_yaml())
