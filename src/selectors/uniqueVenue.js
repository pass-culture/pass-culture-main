import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOfferers from './offerers'

export default createSelector(
  selectOfferers,
  state => state.form,
  (state, ownProps) => ownProps.occasionId,
  (offerers, form, occasionId) => {
    console.log('occasionId', occasionId)
    const offererId = get(form, `occasionsById.${occasionId}.offererId`)
    console.log('offererId', offererId)
    const offerer = offererId && offerers && offerers.find(o => o.id === offererId)
    return offerer &&
      offerer.managedVenues &&
      offerer.managedVenues.length === 1 &&
      offerer.managedVenues[0]
  }
)
