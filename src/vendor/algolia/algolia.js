import algoliasearch from 'algoliasearch'

import {
  WEBAPP_ALGOLIA_APPLICATION_ID,
  WEBAPP_ALGOLIA_INDEX_NAME,
  WEBAPP_ALGOLIA_SEARCH_API_KEY,
} from '../../utils/config'
import { FACETS } from './facets'
import { FILTERS } from './filters'

export const fetchAlgolia = ({
                               aroundRadius = null,
                               categories = [],
                               geolocationCoordinates = null,
                               indexSuffix = '',
                               keywords = '',
                               offerTypes = {
                                 isDigital: false,
                                 isEvent: false,
                                 isThing: false
                               },
                               page = 0,
                             } = {}
) => {
  const searchParameters = {
    page: page,
    ...buildFacetFilters(categories, offerTypes),
    ..._buildGeolocationParameter(geolocationCoordinates, aroundRadius),
  }
  const client = algoliasearch(WEBAPP_ALGOLIA_APPLICATION_ID, WEBAPP_ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(WEBAPP_ALGOLIA_INDEX_NAME + indexSuffix)

  return index.search(keywords, searchParameters)
}

const buildFacetFilters = (categories, offerTypes) => {
  if (categories.length === 0 && offerTypes == null) {
    return
  }

  const facetFilters = []
  if (categories.length > 0) {
    const categoriesPredicate = _buildCategoriesPredicate(categories)
    facetFilters.push(categoriesPredicate)
  }
  const offerTypesPredicate = _buildOfferTypesPredicate(offerTypes)

  if (offerTypesPredicate) {
    facetFilters.push(...offerTypesPredicate)
  }


  return {
    facetFilters,
  }
}

const _buildCategoriesPredicate = categories => {
  return categories.map(category => `${FACETS.OFFER_CATEGORY}:${category}`)
}

const _buildOfferTypesPredicate = offerTypes => {
  const { isDigital, isEvent, isThing } = offerTypes
  if (isDigital) {
    if (!isEvent && !isThing) {
      return [`${FACETS.OFFER_IS_DIGITAL}:${isDigital}`]
    }
    if (!isEvent && isThing) {
      return [`${FACETS.OFFER_IS_THING}:${isThing}`]
    }
    if (isEvent && !isThing) {
      return [[`${FACETS.OFFER_IS_DIGITAL}:${isDigital}`, `${FACETS.OFFER_IS_EVENT}:${isEvent}`]]
    }
  } else {
    if (!isEvent && isThing) {
      return [`${FACETS.OFFER_IS_DIGITAL}:${isDigital}`, `${FACETS.OFFER_IS_THING}:${isThing}`]
    }
    if (isEvent && !isThing) {
      return [`${FACETS.OFFER_IS_EVENT}:${isEvent}`]
    }
    if (isEvent && isThing) {
      return [`${FACETS.OFFER_IS_DIGITAL}:${isDigital}`]
    }
  }
}

const _buildGeolocationParameter = (coordinates, aroundRadius) => {
  if (coordinates) {
    const { longitude, latitude } = coordinates
    if (latitude && longitude) {
      return {
        aroundLatLng: `${latitude}, ${longitude}`,
        aroundRadius: aroundRadius ? aroundRadius * 1000 : FILTERS.UNLIMITED_RADIUS,
      }
    }
  }
}
