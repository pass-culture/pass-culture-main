import { createSelector } from 'reselect'

const emptyOffers = []

export default () => createSelector(
  state => state.data.offers,
  (state, ownProps) => ownProps.id,
  (offers, venueId) =>
    (offers && offers.filter(o => o.venueId === venueId)) || emptyOffers
)
