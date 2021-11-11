import { TOKEN_ACTIONS } from '../actions/token'

const initialState = {
  hasBeenChecked: false,
  isValid: false,
}

const token = (state = initialState, action = {}) => {
  if (action.type === TOKEN_ACTIONS.CHANGE_TOKEN_STATUS) {
    return { ...state, hasBeenChecked: true, isValid: action.payload }
  } else {
    return state
  }
}

export default token
