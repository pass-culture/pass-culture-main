import { createSelector } from 'reselect'
import get from 'lodash.get'

export default () => createSelector(
  state => get(state, 'data.offers', []),
  (state, venueId) => venueId,
  (offers, venueId) => {
    if (!venueId) return offers
    return offers.filter(o => o.venueId === venueId)
  }
)
