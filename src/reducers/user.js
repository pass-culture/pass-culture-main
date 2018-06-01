// ACTIONS
export const SET_USER = 'SET_USER'

// INITIAL STATE
const initialState = null

// REDUCER
function user(state = initialState, action) {
  switch (action.type) {
    case SET_USER:
      return action.user
    default:
      return state
  }
}

// ACTION CREATORS
export function setUser(user) {
  return {
    type: SET_USER,
    user,
  }
}

// default
export default user
