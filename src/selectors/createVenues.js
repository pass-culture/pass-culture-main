import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.venues,
  (state, offererId) => offererId,
  (venues, offererId) => {
    if (offererId)
      return venues.filter(v => v.managingOffererId === offererId)
    return venues
  }
)
