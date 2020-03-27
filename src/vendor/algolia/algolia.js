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
                               geolocation = null,
                               keywords = '',
                               offerCategories = [],
                               offerTypes = {
                                 isDigital: false,
                                 isEvent: false,
                                 isThing: false
                               },
                               page = 0,
                               sortBy = ''
                             } = {}
) => {
  const searchParameters = {
    page: page,
    ...buildFacetFilters(offerCategories, offerTypes),
    ...buildGeolocationParameter(aroundRadius, geolocation),
  }
  const client = algoliasearch(WEBAPP_ALGOLIA_APPLICATION_ID, WEBAPP_ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(WEBAPP_ALGOLIA_INDEX_NAME + sortBy)

  return index.search(keywords, searchParameters)
}

const buildFacetFilters = (offerCategories, offerTypes) => {
  if (offerCategories.length === 0 && offerTypes == null) {
    return
  }

  const facetFilters = []
  if (offerCategories.length > 0) {
    const categoriesPredicate = buildOfferCategoriesPredicate(offerCategories)
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

const buildOfferCategoriesPredicate = offerCategories => {
  return offerCategories.map(category => `${FACETS.OFFER_CATEGORY}:${category}`)
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

const buildGeolocationParameter = (aroundRadius, geolocation) => {
  if (geolocation) {
    const { longitude, latitude } = geolocation
    if (latitude && longitude) {
      const aroundRadiusInMeters = aroundRadius * 1000
      return {
        aroundLatLng: `${latitude}, ${longitude}`,
        aroundRadius: aroundRadius ? aroundRadiusInMeters : FILTERS.UNLIMITED_RADIUS,
      }
    }
  }
}
