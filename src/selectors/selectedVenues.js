import get from 'lodash.get'
import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.venues,
  (state, ownProps) =>
    get(ownProps, 'occasion.occurences.0.venue.managingOffererId') ||
    get(state, `form.occasionsById.${ownProps.occasionId}.offererId`),
  (venues, offererId) => {
    console.log('venues', venues, 'offererId', offererId)
    return venues &&
    venues.filter(v => v.managingOffererId === offererId)
  }
)
