import { SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP } from '../actions/lastRecommendationsRequestTimestamp'

const lastRecommendationsRequestTimestamp = (state = 0, action) => {
  if (action.type === SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP) {
    return Date.now()
  } else {
    return state
  }
}

export default lastRecommendationsRequestTimestamp
