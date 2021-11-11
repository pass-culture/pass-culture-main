import { SET_CURRENT_USER } from '../actions/currentUser'

const initialState = null

function currentUserReducer(state = initialState, action) {
  switch (action.type) {
    case SET_CURRENT_USER:
      return action.value

    default:
      return state
  }
}

export default currentUserReducer
