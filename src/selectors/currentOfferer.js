import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectCurrentOccasion from './currentOccasion'

export default createSelector(
  selectCurrentOccasion,
  (state, ownProps) => ownProps.match.params.occasionPath,
  (occasion, occasionPath) => {
    if (!occasion) { return }
    if (occasionPath === 'evenements') {
      return get(occasion, 'occurences.0.offer.0.offerer')
    }
  }
)
