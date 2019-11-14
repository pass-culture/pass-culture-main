const UPDATE_PAGE = 'UPDATE_PAGE'
const UPDATE_SEED = 'UPDATE_SEED'

const initialState = {
  page: 1,
  seed: Math.random()
}

const paginationReducer = (state = initialState, action = {}) => {
  switch(action.type){
    case UPDATE_PAGE:
      return Object.assign({}, state, { page: action.page })
    case UPDATE_SEED:
      return Object.assign({}, state, { seed: action.seed })
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

export default paginationReducer
