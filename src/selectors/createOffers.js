import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.offers,
  (state, params) => params,
  (offers, {venueId}) => {
    if (venueId)
      offers = offers.filter(o => o.venueId === venueId)
    return offers
  }
)
