import get from 'lodash.get'
import { createSelector } from 'reselect'

export default createSelector(
  (state, event) => event,
  (state, event, thing) => thing,
  (state, event, thing, venue) => venue,
  (event, thing, venue) =>
    Object.assign({}, event || thing, {
      offererId: get(venue, 'managingOffererId'),
      venueId: get(venue, 'id'),
    })
)
