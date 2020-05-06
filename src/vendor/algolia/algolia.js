import { ALGOLIA_APPLICATION_ID, ALGOLIA_INDEX_NAME, ALGOLIA_SEARCH_API_KEY, } from '../../utils/config'
import {
  getFirstTimestampForGivenDate,
  getFirstTimestampOfTheWeekEndForGivenDate,
  getLastTimestampForGivenDate,
  getLastTimestampOfTheWeekForGivenDate,
  getTimestampFromDate,
} from '../../utils/date/date'
import { FACETS } from './facets'
import { DEFAULT_RADIUS_IN_KILOMETERS, FILTERS, RADIUS_IN_METERS_FOR_NO_OFFERS } from './filters'
import algoliasearch from 'algoliasearch'
import { DATE_FILTER } from '../../components/pages/search-algolia/Filters/filtersEnums'

export const fetchAlgolia = ({
                               aroundRadius = DEFAULT_RADIUS_IN_KILOMETERS,
                               date = null,
                               geolocation = null,
                               keywords = '',
                               offerCategories = [],
                               offerIsDuo = false,
                               offerIsFree = false,
                               offerIsNew = false,
                               offerTypes = {
                                 isDigital: false,
                                 isEvent: false,
                                 isThing: false,
                               },
                               page = 0,
                               priceRange = [],
                               sortBy = '',
                               searchAround = false,
                             } = {}) => {
  const searchParameters = {
    page: page,
    ...buildFacetFilters(offerCategories, offerTypes, offerIsDuo),
    ...buildNumericFilters(offerIsFree, priceRange, date, offerIsNew),
    ...buildGeolocationParameter(aroundRadius, geolocation, searchAround),
  }
  const client = algoliasearch(ALGOLIA_APPLICATION_ID, ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(ALGOLIA_INDEX_NAME + sortBy)

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
  if (offerIsDuoPredicate) {
    facetFilters.push(offerIsDuoPredicate)
  }

  const atLeastOneFacetFilter = facetFilters.length > 0
  return atLeastOneFacetFilter ? { facetFilters } : {}
}

const buildNumericFilters = (offerIsFree, priceRange, date, offerIsNew) => {
  const priceRangePredicate = buildOfferPriceRangePredicate(offerIsFree, priceRange)
  const datePredicate = buildDatePredicate(date)
  const newestOffersPredicate = buildNewestOffersPredicate(offerIsNew)
  const numericFilters = []

  if (priceRangePredicate) {
    numericFilters.push(priceRangePredicate)
  }

  if (datePredicate) {
    numericFilters.push(datePredicate)
  }

  if (newestOffersPredicate) {
    numericFilters.push(newestOffersPredicate)
  }

  return numericFilters.length > 0 ? { numericFilters } : {}
}

const buildOfferCategoriesPredicate = offerCategories => {
  return offerCategories.map(category => `${FACETS.OFFER_CATEGORY}:${category}`)
}

const buildOfferIsDuoPredicate = offerIsDuo => {
  if (offerIsDuo) {
    return `${FACETS.OFFER_IS_DUO}:${offerIsDuo}`
  }
}

const buildOfferPriceRangePredicate = (offerIsFree, offerPriceRange) => {
  if (offerIsFree) return `${FACETS.OFFER_PRICE} = 0`
  if (offerPriceRange.length === 2) {
    return `${FACETS.OFFER_PRICE}: ${offerPriceRange.join(' TO ')}`
  }
}

const buildDatePredicate = (date) => {
  if (date) {
    let beginningDate, endingDate
    switch (date.option) {
      case DATE_FILTER.TODAY.value:
        beginningDate = getTimestampFromDate(date.selectedDate)
        endingDate = getLastTimestampForGivenDate(date.selectedDate)
        break
      case DATE_FILTER.CURRENT_WEEK.value:
        beginningDate = getTimestampFromDate(date.selectedDate)
        endingDate = getLastTimestampOfTheWeekForGivenDate(date.selectedDate)
        break
      case DATE_FILTER.CURRENT_WEEK_END.value:
        beginningDate = getFirstTimestampOfTheWeekEndForGivenDate(date.selectedDate)
        endingDate = getLastTimestampOfTheWeekForGivenDate(date.selectedDate)
        break
      case DATE_FILTER.USER_PICK.value:
        beginningDate = getFirstTimestampForGivenDate(date.selectedDate)
        endingDate = getLastTimestampForGivenDate(date.selectedDate)
        break
    }
    return `${FACETS.OFFER_DATE}: ${beginningDate} TO ${endingDate}`
  }
}

const buildNewestOffersPredicate = offerIsNew => {
  if (offerIsNew) {
    const now = new Date()
    const fifteenDaysBeforeNow = new Date().setDate(now.getDate() - 15)
    const beginningDate = getTimestampFromDate(new Date(fifteenDaysBeforeNow))
    const endingDate = getTimestampFromDate(now)

    return `${FACETS.OFFER_STOCKS_DATE_CREATED}: ${beginningDate} TO ${endingDate}`
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

const buildGeolocationParameter = (aroundRadius, geolocation, searchAround) => {
  if (geolocation) {
    const { longitude, latitude } = geolocation
    if (latitude && longitude) {
      const aroundRadiusInMeters = computeRadiusInMeters(aroundRadius, searchAround)

      return {
        aroundLatLng: `${latitude}, ${longitude}`,
        aroundRadius: searchAround ? aroundRadiusInMeters : FILTERS.UNLIMITED_RADIUS
      }
    }
  }
}

const computeRadiusInMeters = (aroundRadius, searchAround) => {
  if (searchAround && aroundRadius === 0) {
    return RADIUS_IN_METERS_FOR_NO_OFFERS
  }
  return aroundRadius * 1000
}
