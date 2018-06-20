import { createSelector } from 'reselect'

import selectOfferererId from './selectedOffererId'
import selectVenues from './venues'

export default createSelector(
  selectVenues,
  selectOfferererId,
  (venues, offererId) =>
    venues && venues.filter(v => v.managingOffererId === offererId)
)
