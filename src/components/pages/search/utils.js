import { pluralize } from 'pass-culture-shared'
import get from 'lodash.get'
import find from 'lodash.find'

const filterIconByState = filters => (filters ? 'filter' : 'filter-active')

export const INITIAL_FILTER_PARAMS = {
  categories: null,
  date: null,
  distance: null,
  jours: null,
  latitude: null,
  longitude: null,
}

export const isSearchFiltersAdded = (initialParams, filterParams) =>
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

export const searchResultsTitle = (keywords, items, queryParams) => {
  let resultTitle
  if (keywords) {
    const count = items.length
    const resultString = pluralize(count, 'résultats')
    const keywordsString = decodeURI(keywords || '')
    const typesString = decodeURI(queryParams.types || '')
    resultTitle = `"${keywordsString}" ${typesString}: ${resultString}`
  }
  return resultTitle
}

// TODO SEARCH FILTER FUNCTIONS REFACTORING

export const handleQueryChange = (newValue, callback) => {
  const { pagination } = this.props
  const { query } = this.state

  const nextFilterParams = Object.assign({}, query, newValue)
  const isNew = getFirstChangingKey(pagination.windowQuery, newValue)

  this.setState(
    {
      isNew,
      query: nextFilterParams,
    },
    callback
  )
}

export const descriptionForSublabel = (category, data) => {
  // TODO continue with special chars...
  const categoryWithoutSpecialChar = category.replace(/%C3%89/g, 'É')
  return find(data, ['sublabel', categoryWithoutSpecialChar]).description
}

// filter = le this.state du composant parent
export const handleQueryAdd = (key, value, filter, callback) => {
  const { query } = filter
  const encodedValue = encodeURI(value)
  let nextValue = encodedValue
  const previousValue = query[key]
  if (get(previousValue, 'length')) {
    const args = previousValue.split(',').concat([encodedValue])
    args.sort()
    nextValue = args.join(',')
  }

  handleQueryChange({ [key]: nextValue }, callback)
}

export default filterIconByState
