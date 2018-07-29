import createCachedSelector from 're-reselect'

import { queryStringToObject } from '../utils/string'

export default createCachedSelector(
  (state, search) => search,
  queryStringToObject
)((state, search) => search || '')
