import { createSelector } from 'reselect'

import selectCurrentOffererId from './currentOffererId'

export default createSelector(
  state => state.data.venues,
  selectCurrentOffererId,
  (venues, offererId) => venues &&
    venues.filter(v => v.managingOffererId === offererId)
)
