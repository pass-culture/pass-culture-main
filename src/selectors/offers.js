import { createSelector } from 'reselect'

// TODO: check if used

const emptyOffers = []

export default () => createSelector(
  state => state.data.offers,
  (state, ownProps) => ownProps.id,
  (offers, venueId) =>
    (offers && offers.filter(o => o.venueId === venueId)) || emptyOffers
)
