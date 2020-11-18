from pcapi.models import Stock
from pcapi.repository import repository
from pcapi.repository.provider_queries import get_provider_by_local_class


def delete_corrupted_allocine_stocks():
    new_stock_id_at_providers_format = "%#%"
    allocine_provider = get_provider_by_local_class("AllocineStocks")
    stocks_to_delete = (
        Stock.query.filter_by(lastProviderId=allocine_provider.id)
        .filter_by(isSoftDeleted=True)
        .filter(Stock.idAtProviders.notilike(new_stock_id_at_providers_format))
        .all()
    )

    repository.delete(*stocks_to_delete)
