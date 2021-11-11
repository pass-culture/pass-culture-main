import { UPDATE_SEED_LAST_REQUEST_TIMESTAMP } from '../actions/pagination'

const initialState = {
  seedLastRequestTimestamp: Date.now(),
}

const pagination = (state = initialState, action = {}) => {
  switch (action.type) {
    case UPDATE_SEED_LAST_REQUEST_TIMESTAMP:
      return Object.assign({}, state, { seedLastRequestTimestamp: action.seedLastRequestTimestamp })
    default:
      return state
  }
}

export default pagination
