import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import selectTypes from './types'

export default createSelector(
  state => state.data.occasions,
  state => state.data.searchedOccasions,
  (occasions, searchedOccasions) => {
    if (!occasions && !searchedOccasions) return

    const filteredOccasions = [...(searchedOccasions || occasions)]

    return filteredOccasions
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
