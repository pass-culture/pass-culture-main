import { createSelector } from 'reselect'

import selectSelectedOffererId from './selectedOffererId'

export default createSelector(
  state => state.data.venues,
  selectSelectedOffererId,
  (venues, offererId) => venues &&
    venues.filter(v => v.managingOffererId === offererId)
)
