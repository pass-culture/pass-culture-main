import { createSelector } from 'reselect'

import { queryStringToObject } from '../utils/string'

export default () => createSelector(
  (_, search) => search,
  queryStringToObject
)
