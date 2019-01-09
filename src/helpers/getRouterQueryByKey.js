import get from 'lodash.get'
import queryString from 'query-string'

const getRouterQueryByKey = (reactRouterLocationObject, stringKey) => {
  if (!reactRouterLocationObject || !stringKey) {
    throw new Error('getRouterQueryByKey: Missing arguments')
  }
  const searchQuery = get(reactRouterLocationObject, 'search') || undefined
  if (!searchQuery) return undefined
  const parsed = queryString.parse(searchQuery)
  const value = get(parsed, stringKey) || undefined
  return value
}

export default getRouterQueryByKey
