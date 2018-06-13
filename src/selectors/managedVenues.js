import get from 'lodash.get'
import { createSelector } from 'reselect'

export default () => createSelector(
  state => state.data.venues,
  (state, ownProps) => get(ownProps, 'offerer.id'),
  (venues, offererId) => venues &&
    venues.filter(v => v.managingOffererId === offererId)
)
