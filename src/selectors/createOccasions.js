import get from 'lodash.get'
import { createSelector } from 'reselect'

export default () => createSelector(
  state => get(state, 'data.searchedOccasions', get(state, 'data.occasions', [])),
  (_, params) => params,
  (occasions, {offererId, venueId}={}) => {
    if (offererId)
      occasions = occasions.filter(o => o.lastProviderId === offererId)

    // TODO: find the link between occasion and venue
    if (venueId)
      occasions = occasions.filter(o => o.venueId === venueId)

    return occasions
      .sort((o1, o2) => o1.dehumanizedId - o2.dehumanizedId)
  }
)
