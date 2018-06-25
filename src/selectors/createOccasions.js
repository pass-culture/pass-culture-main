import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import selectTypes from './types'

export default () => createSelector(
  state => get(state, 'data.searchedOccasions', get(state, 'data.occasions', [])),
  (state, venueId) => venueId,
  (occasions, venueId) => {
    if (venueId)
      occasions = occasions.filter(o => o.venueId === venueId)

    return occasions
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
