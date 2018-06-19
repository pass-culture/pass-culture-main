import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOfferers from './offerers'
import { NEW } from '../utils/config'

export default createSelector(
  selectOfferers,
  (state, ownProps) => get(ownProps, 'currentOccasion.offererId'),
  (state, ownProps) => get(ownProps, 'currentOccasion.id'),
  (state, ownProps) => get(state, 'form.occasionsById'),
  (offerers, currentOffererId, currentOccasionId, occasionsById) => {
    const formOccasion = get(occasionsById, currentOccasionId || NEW)
    return get(formOccasion, 'offererId') || 
      currentOffererId ||
      (get(offerers, 'length') === 1 && get(offerers, '0.id'))
  }
)
