import { createSelector } from 'reselect'

import { NEW } from '../utils/config'

export default createSelector(
  (state, ownProps) =>
    get(ownProps, 'occasion.occurences.0.venue.managingOffererId') ||
    get(state, `form.occasionsById.${NEW}.offererId`),
  (state, ownProps) => ownProps.match.params.occasionId,
  (occasionsById, occasionId) => occasionsById && occasionId === 'nouveau'
    ? occasionsById[NEW]
    : occasionsById[occasionId]
)
