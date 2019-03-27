const initialState = {
  hasBeenChecked: false,
  isValid: false,
}

const tokenReducer = (state = initialState, action = {}) => {
  switch (action.type) {
    default:
      return state
  }
}

export function setTokenStatus(tokenStatus) {
  return { payload: tokenStatus, type: 'SET_TOKEN_STATUS' }
}

export default tokenReducer
