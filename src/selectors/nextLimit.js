import { createSelector } from 'reselect'

import { PREVIOUS_NEXT_LIMIT } from '../utils/deck'

export default createSelector(
  state => state.data.userMediations,
  userMediations => {
    return userMediations && (
      PREVIOUS_NEXT_LIMIT >= userMediations.length - 1
        ? userMediations.length - 1
        : userMediations.length - 1 - PREVIOUS_NEXT_LIMIT
    )
  }
)
