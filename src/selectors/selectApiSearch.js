import { searchSelector } from 'pass-culture-shared'
import createCachedSelector from 're-reselect'

import { windowToApiQuery } from '../utils/pagination'

const mapArgsToKey = (state, search) => search

const selectApiSearch = createCachedSelector(searchSelector, windowToApiQuery)(
  mapArgsToKey
)

export default selectApiSearch
