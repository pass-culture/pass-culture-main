import get from 'lodash.get'
import { createSelector } from 'reselect'

const createSelectVenues = () => createSelector(
  state => (console.log(state.data.venues, state) && get(state, 'data.venues', [])),
  (state, params) => params,
  (venues, {offererId}) => {
    console.log(venues, offererId)
    // if (offererId)
    //   return venues.filter(v => v.managingOffererId === offererId)

    return venues
  }
)
export default createSelectVenues

