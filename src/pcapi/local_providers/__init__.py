from pcapi.local_providers.allocine.allocine_stocks import AllocineStocks
from pcapi.local_providers.libraires.libraires_stocks import LibrairesStocks
from pcapi.local_providers.titelive_stocks.titelive_stocks import TiteLiveStocks
from pcapi.local_providers.titelive_thing_descriptions.titelive_thing_descriptions import TiteLiveThingDescriptions
from pcapi.local_providers.titelive_thing_thumbs.titelive_thing_thumbs import TiteLiveThingThumbs
from pcapi.local_providers.titelive_things.titelive_things import TiteLiveThings
from pcapi.local_providers.fnac.fnac_stocks import FnacStocks
from pcapi.local_providers.praxiel.praxiel_stocks import PraxielStocks

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
