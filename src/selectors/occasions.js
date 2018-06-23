import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import selectTypes from './types'

export default createSelector(
  state => state.data.occasions,
  state => state.data.searchedOccasions,
  (state, ownProps) => get(ownProps, 'match.params.venueId'),
  (occasions, searchedOccasions, venueId) => {
    if (!occasions && !searchedOccasions) return

    let filteredOccasions = [...(searchedOccasions || occasions)]

    if (venueId) {
      filteredOccasions = filteredOccasions.filter(o => o.venueId === venueId)
    }

    return filteredOccasions
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
