import {
  capitalize,
  pluralize,
  getObjectWithMappedKeys,
} from 'pass-culture-shared'
import find from 'lodash.find'
import get from 'lodash.get'
import moment from 'moment'

import { getTimezone } from '../../../utils/timezone'
import { isEmpty } from '../../../utils/strings'

export const INITIAL_FILTER_PARAMS = {
  categories: null,
  date: null,
  distance: null,
  jours: null,
  latitude: null,
  longitude: null,
  [`mots-cles`]: null,
  page: null,
}

export const DAYS_CHECKBOXES = [
  {
    label: 'Tout de suite !',
    value: '0-1',
  },
  {
    label: 'Entre 1 et 5 jours',
    value: '1-5',
  },
  {
    label: 'Plus de 5 jours',
    // will the pass culture live for ever?
    // guess that 273 years are enough
    value: '5-100000',
  },
]

const isInitialQueryWithoutFilters = (initialParams, filterParams) =>
  Object.keys(initialParams).every(
    key =>
      typeof filterParams[key] === 'undefined' ||
      filterParams[key] === null ||
      filterParams[key] === ''
  )

export const getFirstChangingKey = (previousObject, nextObject) =>
  Object.keys(nextObject).find(key => {
    const isNewFalsy = nextObject[key] === null || nextObject[key] === ''
    const isPreviousFalsy =
      typeof previousObject[key] === 'undefined' ||
      previousObject[key] === null ||
      previousObject === ''
    if (isNewFalsy && isPreviousFalsy) {
      return false
    }
    return previousObject[key] !== nextObject[key]
  })

export const searchResultsTitle = (
  keywords,
  items,
  queryParams,
  cameFromOfferTypesPage = false,
  hasReceivedFirstSuccessData
) => {
  if (!hasReceivedFirstSuccessData) {
    return ''
  }
  let resultTitle
  if (cameFromOfferTypesPage) {
    resultTitle =
      items.length === 0
        ? "Il n'y a pas d'offres dans cette catégorie pour le moment."
        : ''
  } else {
    const count = items.length
    const resultString = pluralize(count, 'résultats')
    const keywordsString = decodeURI(keywords || '')
    const typesString = decodeURI(queryParams.types || '')

    if (isEmpty(keywordsString)) {
      resultTitle = ''
    } else {
      resultTitle = `"${keywordsString}" ${typesString}: ${resultString}`
    }
  }

  return resultTitle
}

const formatDate = (date, tz) =>
  capitalize(
    moment(date)
      .tz(tz)
      .format('dddd DD/MM/YYYY')
  )

export const getRecommendationDateString = offer => {
  if (offer.eventId === null) return 'permanent'
  const departementCode = offer.venue.departementCode
  const tz = getTimezone(departementCode)

  const fromDate = offer.dateRange[0]
  const toDate = offer.dateRange[1]
  const formatedDate = `du ${formatDate(fromDate, tz)} au ${formatDate(
    toDate,
    tz
  )}`
  return formatedDate
}

export const getDescriptionForSublabel = (category, data) =>
  get(find(data, ['sublabel', category]), 'description')

const mapWindowToApi = {
  jours: 'days',
  'mots-cles': 'keywords',
}

export const translateBrowserUrlToApiUrl = query =>
  getObjectWithMappedKeys(query, mapWindowToApi)

export default isInitialQueryWithoutFilters
