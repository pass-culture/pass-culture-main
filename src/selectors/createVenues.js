import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectSelectedOfferererId from './selectedOffererId'

const createSelectVenues = () => createSelector(
  state => get(state, 'data.venues', []),
  (state, offererId) => offererId,
  (venues, offererId) => {
    if (!offererId) return venues
    return venues.filter(v => v.managingOffererId === offererId)
  }
)
export default createSelectVenues

// Don't do that: exports are cached, so the method is called only once
// export const selectVenues = createSelectVenues()
