import { requestData } from 'redux-thunk-data'

const TOKEN_ACTIONS = {
  CHANGE_TOKEN_STATUS: 'SET_TOKEN_STATUS',
}

const initialState = {
  hasBeenChecked: false,
  isValid: false,
}

// Reducer
const tokenReducer = (state = initialState, action = {}) => {
  switch (action.type) {
    case TOKEN_ACTIONS.CHANGE_TOKEN_STATUS:
      return { ...state, hasBeenChecked: true, isValid: action.payload }
    default:
      return state
  }
}

export const validateToken = (token, dispatch) => {
  const tokenValidityRequest = new Promise((resolve, reject) => {
    dispatch(
      requestData({
        apiPath: `/users/token/${token}`,
        handleFail: reject,
        handleSuccess: resolve,
        method: 'GET',
      })
    )
  })

  return tokenValidityRequest.then(() => true).catch(() => false)
}

// Actions
export function setTokenStatus(tokenStatus) {
  return { payload: tokenStatus, type: TOKEN_ACTIONS.CHANGE_TOKEN_STATUS }
}

export default tokenReducer
