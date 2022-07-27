import { createCachedSelector } from 're-reselect'

import { parse } from 'utils/query-string'

export const searchSelector = createCachedSelector(
  (state, search) => search,

  search => parse(search) || {}
)((state, search) => search || '')
