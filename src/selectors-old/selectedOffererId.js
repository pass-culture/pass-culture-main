import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectOfferers from './offerers'
import selectFormOccasion from './formOccasion'

export default createSelector(
  selectOfferers,
  selectFormOccasion,
  (state, ownProps) => get(ownProps, 'currentOccasion.offererId'),
  (offerers, formOccasion, currentOffererId) => {
    return get(formOccasion, 'offererId') ||
      currentOffererId ||
      (get(offerers, 'length') === 1 && get(offerers, '0.id'))
  }
)
