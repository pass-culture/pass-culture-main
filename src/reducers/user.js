// ACTIONS
export const SET_USER = 'SET_USER'
export const SET_USER_OFFERER = 'SET_USER_OFFERER'

// INITIAL STATE
const initialState = null

// REDUCER
function user (state = initialState, action) {
  switch (action.type) {
    case SET_USER:
      return action.user && Object.assign({
        isPro: action.user && action.user.userOfferers && action.user.userOfferers[0]
      }, action.user)
    case SET_USER_OFFERER:
      if (!state) {
        return state
      }
      return Object.assign({}, state, {
        offerer: state.userOfferers.find(({ id }) => id === action.id)
      })
    default:
      return state
  }
}

// ACTION CREATORS
export function setUser (user) {
  return {
    type: SET_USER,
    user
  }
}

export function setUserOfferer (id) {
  return {
    type: SET_USER_OFFERER,
    id
  }
}

// default
export default user
