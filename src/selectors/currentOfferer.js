import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectCurrentOccasion from './currentOccasion'
import selectOfferers from './offerers'

export default createSelector(
  selectCurrentOccasion,
  selectOfferers,
  (state, ownProps) => ownProps.match.params.offererId,
  (state, ownProps) => ownProps.match.params.occasionPath,
  (occasion, offerers, offererId, occasionPath) => {
    if (offererId) {
      console.log('---------- selectCurrentOfferer ------------', offerers)
      return offerers && offerers.find(o => o.id === offererId)
    }
    if (!occasion) { return }
    if (occasionPath === 'evenements') {
      return get(occasion, 'occurences.0.offer.0.offerer')
    }
  }
)
