import { createSelector } from 'reselect'

import { PREVIOUS_NEXT_LIMIT } from '../utils/deck'

export default createSelector(
  state => state.data.recommendations,
  recommendations => {
    return (
      recommendations &&
      (PREVIOUS_NEXT_LIMIT >= recommendations.length - 1
        ? recommendations.length - 1
        : recommendations.length - 1 - PREVIOUS_NEXT_LIMIT)
    )
  }
)
