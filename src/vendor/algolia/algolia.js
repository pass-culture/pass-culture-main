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
                               offerIsDuo = false,
                               offerIsFree = false,
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
    ...buildFacetFilters(offerCategories, offerTypes, offerIsDuo),
    ...buildNumericFilters(offerIsFree),
    ...buildGeolocationParameter(aroundRadius, geolocation),
  }
  const client = algoliasearch(WEBAPP_ALGOLIA_APPLICATION_ID, WEBAPP_ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(WEBAPP_ALGOLIA_INDEX_NAME + sortBy)

  return index.search(keywords, searchParameters)
}

const buildFacetFilters = (offerCategories, offerTypes, offerIsDuo) => {
  if (offerCategories.length === 0 && offerTypes == null && offerIsDuo === false) {
    return
  }

  const facetFilters = []

  if (offerCategories.length > 0) {
    const categoriesPredicate = buildOfferCategoriesPredicate(offerCategories)
    facetFilters.push(categoriesPredicate)
  }

  const offerTypesPredicate = buildOfferTypesPredicate(offerTypes)
  if (offerTypesPredicate) {
    facetFilters.push(...offerTypesPredicate)
  }

  const offerIsDuoPredicate = buildOfferIsDuoPredicate(offerIsDuo)
  if (offerIsDuoPredicate){
    facetFilters.push(offerIsDuoPredicate)
  }

  const atLeastOneFacetFilter = facetFilters.length > 0
  return atLeastOneFacetFilter ? { facetFilters } : {}
}

const buildNumericFilters = offerIsFree => {
  const numericFilters = []
  const offerIsFreePredicate = buildOfferIsFreePredicate(offerIsFree)
  if (offerIsFreePredicate){
    numericFilters.push(offerIsFreePredicate)
  }

  const atListOneNumericFilter = numericFilters.length > 0
  return atListOneNumericFilter ? { numericFilters } : {}
}

const buildOfferCategoriesPredicate = offerCategories => {
  return offerCategories.map(category => `${FACETS.OFFER_CATEGORY}:${category}`)
}

const buildOfferIsDuoPredicate = offerIsDuo => {
  if (offerIsDuo) {
    return `${FACETS.OFFER_IS_DUO}:${offerIsDuo}`
  }
}

const buildOfferIsFreePredicate = offerIsFree => {
  if (offerIsFree) {
    return `${FACETS.OFFER_IS_FREE} = 0`
  }
}

const buildOfferTypesPredicate = offerTypes => {
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
