import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectSelectedOfferererId from './selectedOffererId'

const createSelectVenues = () => createSelector(
  state => state.data.venues,
  (state, ownProps) => get(ownProps, 'match.params.offererId'),
  (state, ownProps) => get(ownProps, 'offerer.id'),
  selectSelectedOfferererId,
  (venues, matchOffererId, propsOffererId, selectedOffererId) => {
    if (!venues) {
      return
    }

    let filteredVenues = [...venues]

    if (matchOffererId || propsOffererId || selectedOffererId) {
      filteredVenues = filteredVenues.filter(v =>
        v.managingOffererId === (matchOffererId || propsOffererId || selectedOffererId))
    }

    return filteredVenues
  }
)
export default createSelectVenues

export const selectVenues = createSelectVenues()
