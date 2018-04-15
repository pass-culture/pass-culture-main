import { createSelector } from 'reselect'

import selectUserMediation from './userMediation'

export default createSelector(
  state => state.data.userMediations,
  state => selectUserMediation(state),
  (userMediations, userMediation) =>
    userMediation
    && userMediations
    && userMediations[userMediations.findIndex(um => um.id === userMediation.id) + 1]
)
