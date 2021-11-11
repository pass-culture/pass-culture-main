import { FEATURES_FETCH_FAILED } from '../actions/features'

const initialState = { fetchHasFailed: false }

const features = (state = initialState, action) => {
  if (action.type === FEATURES_FETCH_FAILED) {
    return { fetchHasFailed: true }
  } else {
    return state
  }
}

export default features
