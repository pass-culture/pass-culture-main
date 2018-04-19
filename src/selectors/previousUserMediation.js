import { createSelector } from 'reselect'

import selectCurrentUserMediation from './currentUserMediation'
import getUserMediation from '../getters/userMediation'

export default createSelector(
  state => state.data.userMediations,
  selectCurrentUserMediation,
  (userMediations, currentUserMediation) => {
    const previousUserMediation =
      currentUserMediation &&
      userMediations &&
      userMediations[
        userMediations.findIndex(um => um.id === currentUserMediation.id) - 1
      ]
    return getUserMediation({ userMediation: previousUserMediation })
  }
)
