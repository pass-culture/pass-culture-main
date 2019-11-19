const UPDATE_PAGE = 'UPDATE_PAGE'
const UPDATE_SEED = 'UPDATE_SEED'
const UPDATE_SEED_LAST_REQUEST_TIMESTAMP = 'UPDATE_SEED_LAST_REQUEST_TIMESTAMP'

const initialState = {
  page: 1,
  seed: Math.random(),
  seedLastRequestTimestamp: Date.now()
}

const paginationReducer = (state = initialState, action = {}) => {
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

export const updatePage = (page) => ({
  page,
  type: UPDATE_PAGE,
})

export const updateSeed = (seed) => ({
  seed,
  type: UPDATE_SEED,
})

export const updateSeedLastRequestTimestamp = (seedLastRequestTimestamp) => ({
  seedLastRequestTimestamp,
  type: UPDATE_SEED_LAST_REQUEST_TIMESTAMP,
})

export default paginationReducer
