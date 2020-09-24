from local_providers.allocine.allocine_stocks import AllocineStocks
from local_providers.libraires.libraires_stocks import LibrairesStocks
from local_providers.titelive_stocks.titelive_stocks import TiteLiveStocks
from local_providers.titelive_thing_descriptions.titelive_thing_descriptions import TiteLiveThingDescriptions
from local_providers.titelive_thing_thumbs.titelive_thing_thumbs import TiteLiveThingThumbs
from local_providers.titelive_things.titelive_things import TiteLiveThings
from local_providers.fnac.fnac_stocks import FnacStocks
from local_providers.praxiel.praxiel_stocks import PraxielStocks

__all__ = (
    'TiteLiveStocks',
    'TiteLiveThings',
    'TiteLiveThingDescriptions',
    'TiteLiveThingThumbs',
    'AllocineStocks',
    'LibrairesStocks',
    'FnacStocks',
    'PraxielStocks'
)
