import algoliasearch from 'algoliasearch'
import { DATE_FILTER } from '../../components/pages/search/Filters/filtersEnums'
import {
  computeTimeRangeFromHoursToSeconds,
  TIMESTAMP,
} from '../../components/pages/search/utils/date/time'
import {
  ALGOLIA_APPLICATION_ID,
  ALGOLIA_INDEX_NAME,
  ALGOLIA_SEARCH_API_KEY,
} from '../../utils/config'
import { FACETS } from './facets'
import { DEFAULT_RADIUS_IN_KILOMETERS, FILTERS, RADIUS_IN_METERS_FOR_NO_OFFERS } from './filters'

export const fetchAlgolia = ({
  aroundRadius = DEFAULT_RADIUS_IN_KILOMETERS,
  beginningDatetime = null,
  date = null,
  endingDatetime = null,
  geolocation = null,
  hitsPerPage = null,
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
  searchAround = false,
  tags = [],
  timeRange = [],
} = {}) => {
  const searchParameters = {
    page,
    ...buildFacetFilters({ offerCategories, offerTypes, offerIsDuo, tags }),
    ...buildNumericFilters({
      beginningDatetime,
      date,
      endingDatetime,
      offerIsFree,
      offerIsNew,
      priceRange,
      timeRange,
    }),
    ...buildGeolocationParameter(aroundRadius, geolocation, searchAround),
  }
  if (hitsPerPage) {
    searchParameters.hitsPerPage = hitsPerPage
  }
  const client = algoliasearch(ALGOLIA_APPLICATION_ID, ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(ALGOLIA_INDEX_NAME)

  return index.search(keywords, searchParameters)
}

export const fetchAlgoliaHits = objectIds => {
  const client = algoliasearch(ALGOLIA_APPLICATION_ID, ALGOLIA_SEARCH_API_KEY)
  const index = client.initIndex(ALGOLIA_INDEX_NAME)

  return index.getObjects(objectIds)
}

const buildFacetFilters = ({ offerCategories, offerTypes, offerIsDuo, tags }) => {
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

  const tagsPredicate = buildTagsPredicate(tags)
  if (tagsPredicate) {
    facetFilters.push(tagsPredicate)
  }

  const atLeastOneFacetFilter = facetFilters.length > 0
  return atLeastOneFacetFilter ? { facetFilters } : {}
}

const buildNumericFilters = ({
  beginningDatetime,
  date,
  endingDatetime,
  offerIsFree,
  offerIsNew,
  priceRange,
  timeRange,
}) => {
  const priceRangePredicate = buildOfferPriceRangePredicate(offerIsFree, priceRange)
  const datePredicate = buildDatePredicate(date, timeRange)
  const homepageDatePredicate = buildHomepageDatePredicate(beginningDatetime, endingDatetime)
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

  if (homepageDatePredicate) {
    numericFilters.push(homepageDatePredicate)
  }

  return numericFilters.length > 0 ? { numericFilters } : {}
}

const buildOfferCategoriesPredicate = searchGroups =>
  searchGroups.map(searchGroup => `${FACETS.OFFER_SEARCH_GROUP_NAME}:${searchGroup}`)

const buildOfferIsDuoPredicate = offerIsDuo => {
  if (offerIsDuo) {
    return `${FACETS.OFFER_IS_DUO}:${offerIsDuo}`
  }
}

const buildOfferPriceRangePredicate = (offerIsFree, offerPriceRange) => {
  if (offerIsFree) return `${FACETS.OFFER_PRICES} = 0`
  if (offerPriceRange.length === 2) {
    return `${FACETS.OFFER_PRICES}: ${offerPriceRange.join(' TO ')}`
  }
}

const buildTimeOnlyPredicate = timeRange => {
  const timeRangeInSeconds = computeTimeRangeFromHoursToSeconds(timeRange)
  return `${FACETS.OFFER_TIMES}: ${timeRangeInSeconds.join(' TO ')}`
}

const buildDatePredicate = (date, timeRange) => {
  if (date && timeRange.length > 0) {
    return buildDateAndTimePredicate(date, timeRange)
  } else if (date) {
    return buildDateOnlyPredicate(date)
  } else if (timeRange.length > 0) {
    return buildTimeOnlyPredicate(timeRange)
  }
}

const buildHomepageDatePredicate = (beginningDatetime, endingDatetime) => {
  const noDatePredicate = !beginningDatetime && !endingDatetime
  const fromDatePredicate = beginningDatetime && !endingDatetime
  const untilDatePredicate = !beginningDatetime && endingDatetime
  const beginningTimestamp = beginningDatetime ? TIMESTAMP.getFromDate(beginningDatetime) : null
  const endingTimestamp = endingDatetime ? TIMESTAMP.getFromDate(endingDatetime) : null

  if (noDatePredicate) {
    return null
  }

  if (fromDatePredicate) {
    return `${FACETS.OFFER_DATES} >= ${beginningTimestamp}`
  }

  if (untilDatePredicate) {
    return `${FACETS.OFFER_DATES} <= ${endingTimestamp}`
  }

  return getDatePredicate(beginningTimestamp, endingTimestamp)
}

const getDatePredicate = (lowerDate, higherDate) =>
  `${FACETS.OFFER_DATES}: ${lowerDate} TO ${higherDate}`

const buildDateAndTimePredicate = (date, timeRange) => {
  let dateFilter, rangeTimestamps
  switch (date.option) {
    case DATE_FILTER.CURRENT_WEEK.value:
      dateFilter = TIMESTAMP.WEEK.getAllFromTimeRangeAndDate(
        date.selectedDate,
        timeRange
      ).map(timestampsRangeForADay =>
        getDatePredicate(timestampsRangeForADay[0], timestampsRangeForADay[1])
      )
      break
    case DATE_FILTER.CURRENT_WEEK_END.value:
      dateFilter = TIMESTAMP.WEEK_END.getAllFromTimeRangeAndDate(
        date.selectedDate,
        timeRange
      ).map(timestampsRangeForADay =>
        getDatePredicate(timestampsRangeForADay[0], timestampsRangeForADay[1])
      )
      break
    default:
      rangeTimestamps = TIMESTAMP.getAllFromTimeRangeAndDate(date.selectedDate, timeRange)
      dateFilter = getDatePredicate(rangeTimestamps[0], rangeTimestamps[1])
  }
  return dateFilter
}

const buildDateOnlyPredicate = date => {
  let beginningDate, endingDate
  switch (date.option) {
    case DATE_FILTER.TODAY.value:
      beginningDate = TIMESTAMP.getFromDate(date.selectedDate)
      endingDate = TIMESTAMP.getLastOfDate(date.selectedDate)
      break
    case DATE_FILTER.CURRENT_WEEK.value:
      beginningDate = TIMESTAMP.getFromDate(date.selectedDate)
      endingDate = TIMESTAMP.WEEK.getLastFromDate(date.selectedDate)
      break
    case DATE_FILTER.CURRENT_WEEK_END.value:
      beginningDate = TIMESTAMP.WEEK_END.getFirstFromDate(date.selectedDate)
      endingDate = TIMESTAMP.WEEK.getLastFromDate(date.selectedDate)
      break
    case DATE_FILTER.USER_PICK.value:
      beginningDate = TIMESTAMP.getFirstOfDate(date.selectedDate)
      endingDate = TIMESTAMP.getLastOfDate(date.selectedDate)
      break
  }
  return getDatePredicate(beginningDate, endingDate)
}

const buildNewestOffersPredicate = offerIsNew => {
  if (offerIsNew) {
    const now = new Date()
    const fifteenDaysBeforeNow = new Date().setDate(now.getDate() - 15)
    const beginningDate = TIMESTAMP.getFromDate(new Date(fifteenDaysBeforeNow))
    const endingDate = TIMESTAMP.getFromDate(now)

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
  if (!geolocation) return
  const { latitude, longitude } = geolocation
  if (!latitude || !longitude) return

  return {
    aroundLatLng: `${latitude}, ${longitude}`,
    aroundRadius: computeAroudRadiusInMeters(aroundRadius, searchAround),
  }
}

const computeAroudRadiusInMeters = (aroundRadius, searchAround) => {
  if (!searchAround || aroundRadius === null) return FILTERS.UNLIMITED_RADIUS
  if (aroundRadius === 0) return RADIUS_IN_METERS_FOR_NO_OFFERS
  return aroundRadius * 1000
}

const buildTagsPredicate = tags => {
  if (tags.length > 0) {
    return tags.map(tag => `${FACETS.OFFER_TAGS}:${tag}`)
  }
}
