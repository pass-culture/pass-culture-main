import datetime
import decimal
import logging

import yaml
from sqlalchemy.dialects import postgresql
from open_data_contract_standard.model import OpenDataContractStandard
from open_data_contract_standard.model import SchemaObject
from open_data_contract_standard.model import SchemaProperty
from open_data_contract_standard.model import DataQuality
from open_data_contract_standard.model import Server

from pcapi.core.offers.models import Offer
from pcapi.models import Model as PCAPIModel
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)

def _get_local_server() -> Server:
    return Server(
        id='local',
        server='local',
        type="postgres",
        host='localhost',
        port=5434,
        database='pass_culture',
        schema='public'
    )

PYTHON_TYPE_TO_LOGICAL_TYPE = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    decimal.Decimal: "number",
    datetime.date: "date",
    datetime.datetime: "timestamp",
    datetime.time: "time",
    dict: "object",
    list: "array",
}


def _get_logical_type(python_type: type) -> str | None:
    return PYTHON_TYPE_TO_LOGICAL_TYPE.get(python_type)

def _get_schema_property(column) -> SchemaProperty:
    try: 
        python_type = column.type.python_type
    except NotImplementedError:
        python_type = None
    try: 
        valid_values = list(column.type.python_type.__members__.keys())
    except (AttributeError, NotImplementedError): 
        valid_values = None

    schema_kwargs = dict(
        name=column.name, 
        physicalType=str(column.type.compile(dialect=postgresql.dialect())),
        required=str(not column.nullable),
        primaryKey=str(column.primary_key),
    )
    if valid_values:
        schema_kwargs["quality"] = [DataQuality(
            type="library",
            description=f"Ensure that there are no unexpected {column.name} values.",
            metric="invalidValues",
            arguments={"validValues": valid_values},
            mustBe=0
        )]
    if python_type:
        logical_type = _get_logical_type(python_type)
        if logical_type:
            schema_kwargs["logicalType"] = logical_type
        
    return SchemaProperty(**schema_kwargs)

# Create a custom class that implements import_source method
def _get_datacontract_standard(model: type[PCAPIModel]) -> OpenDataContractStandard:
    open_data_contract = OpenDataContractStandard(
        kind="DataContract",
        id=model.__tablename__,
        name=model.__tablename__,
        version="1.O.0",
        apiVersion="v3.1.0",
        status="draft",
        description={"purpose": "", "limitations": "", "usage": ""},
    )
    open_data_contract.schema_ = []

    columns_schemas = []
    for column in model.__table__.columns:
        schema_property = _get_schema_property(column)

        columns_schemas.append(schema_property)
  

    open_data_contract.schema_.append(SchemaObject(name=model.__tablename__, properties=columns_schemas))
    open_data_contract.servers = [_get_local_server()]
    
    return open_data_contract


class IndentedListDumper(yaml.Dumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow, False)


@blueprint.cli.command("generate_datacontract")
def generate_datacontract() -> None:
    models = [Offer]
    for model in models:
        data_contract_standard = _get_datacontract_standard(model)
        output = yaml.dump(
            data_contract_standard.model_dump(exclude_none=True, by_alias=True),
            Dumper=IndentedListDumper,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
        )
        print(output)


# docker exec pc-api bash -c "cd /usr/src/app/ && flask generate_datacontract" > api/src/pcapi/datacontracts/odcs/offer.yaml
# datacontract import --format odcs --source api/src/pcapi/datacontracts/odcs/offer.yaml > api/src/pcapi/datacontracts/offer_dcs.yaml     
# DATACONTRACT_POSTGRES_USERNAME=pass_culture DATACONTRACT_POSTGRES_PASSWORD=passq datacontract test api/src/pcapi/datacontracts/offer_dcs.yaml     
# DATACONTRACT_POSTGRES_USERNAME=pass_culture 
# DATACONTRACT_POSTGRES_PASSWORD=passq 