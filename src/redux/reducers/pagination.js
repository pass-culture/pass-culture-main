import { UPDATE_PAGE, UPDATE_SEED, UPDATE_SEED_LAST_REQUEST_TIMESTAMP } from '../actions/pagination'

const initialState = {
  page: 1,
  seed: Math.random(),
  seedLastRequestTimestamp: Date.now()
}

const pagination = (state = initialState, action = {}) => {
  switch(action.type){
    case UPDATE_PAGE:
      return Object.assign({}, state, { page: action.page })
    case UPDATE_SEED:
      return Object.assign({}, state, { seed: action.seed })
    case UPDATE_SEED_LAST_REQUEST_TIMESTAMP:
      return Object.assign({}, state, { seedLastRequestTimestamp: action.seedLastRequestTimestamp })
    default:
      return state
  }
}

export default pagination
