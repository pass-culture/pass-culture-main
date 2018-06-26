import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.venues,
  (state, params) => params,
  (venues, {offererId}={}) => {
    if (offererId)
      venues = venues.filter(v => v.managingOffererId === offererId)
    return venues
  }
)
