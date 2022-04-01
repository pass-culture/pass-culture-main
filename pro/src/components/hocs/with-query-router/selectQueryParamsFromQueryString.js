import { createCachedSelector } from 'store/utils'
import { parse } from 'utils/query-string'

function mapArgsToCacheKey(queryString) {
  return queryString
}

export const selectQueryParamsFromQueryString = createCachedSelector(
  queryString => queryString,
  queryString => parse(queryString)
)(mapArgsToCacheKey)

export default selectQueryParamsFromQueryString
