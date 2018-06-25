import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

import selectTypes from './types'

export default () => createSelector(
  state => get(state, 'data.searchedOccasions', get(state, 'data.occasions', [])),
  (_, offererId) => offererId,
  (_, __, venueId) => venueId,
  (occasions, offererId, venueId) => {
    if (offererId)
      occasions = occasions.filter(o => o.lastProviderId === offererId)

    // TODO: find the link between occasion and venue
    if (venueId)
      occasions = occasions.filter(o => o.venueId === venueId)

    return occasions
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
