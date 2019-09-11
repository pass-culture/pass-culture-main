import { pluralize } from 'react-final-form-utils'
import { getObjectWithMappedKeys } from 'with-query-router'

import { isEmpty } from '../../../utils/strings'

export const INITIAL_FILTER_PARAMS = {
  categories: null,
  date: null,
  distance: null,
  jours: null,
  latitude: null,
  longitude: null,
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

const DEFAULT_MAX_DISTANCE = '20000'
const hiddenFilterParams = ['date', 'latitude', 'longitude', 'mots-cles', 'page']
const isVisibleKey = key => !hiddenFilterParams.includes(key)
const isEmptyParam = (key, value) => {
  if (key === 'distance') {
    return value !== null && value !== DEFAULT_MAX_DISTANCE
  }
  return value !== null
}
export const getVisibleParamsAreEmpty = params => {
  const firstEmptyKeyParam = Object.keys(params)
    .filter(isVisibleKey)
    .find(key => isEmptyParam(key, params[key]))
  const paramsAreEmpty = typeof firstEmptyKeyParam === 'undefined'
  return paramsAreEmpty
}

export const isInitialQueryWithoutFilters = (initialParams, filterParams) =>
  Object.keys(initialParams).every(
    key =>
      typeof filterParams[key] === 'undefined' ||
      filterParams[key] === null ||
      filterParams[key] === ''
  )

export const searchResultsTitle = (
  keywords,
  items,
  cameFromOfferTypesPage = false,
  hasReceivedFirstSuccessData
) => {
  if (!hasReceivedFirstSuccessData) {
    return ''
  }
  let resultTitle
  if (cameFromOfferTypesPage) {
    resultTitle =
      items.length === 0 ? 'Il n’y a pas d’offres dans cette catégorie pour le moment.' : ''
  } else {
    const count = items.length
    const resultString = pluralize(count, 'résultats')
    const keywordsString = decodeURI(keywords || '')

    if (isEmpty(keywordsString)) {
      resultTitle = `${resultString}`
    } else {
      resultTitle = `"${keywordsString}" : ${resultString}`
    }
  }

  return resultTitle
}

export const getDescriptionFromCategory = (categoryName, categories) => {
  const goodCategory = categories.find(category => category.sublabel === categoryName)

  return goodCategory ? goodCategory.description : ''
}

const mapWindowToApi = {
  jours: 'days',
  'mots-cles': 'keywords',
}

export const translateBrowserUrlToApiUrl = query => getObjectWithMappedKeys(query, mapWindowToApi)

export const isDaysChecked = (pickedDate, pickedDaysInQuery = '0-1', inputValue = '0-1') => {
  if (pickedDate !== null) return false

  return pickedDaysInQuery.includes(inputValue)
}

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
