import { requestData } from 'redux-thunk-data'

export const TOKEN_ACTIONS = {
  CHANGE_TOKEN_STATUS: 'SET_TOKEN_STATUS',
}

export const setTokenStatus = tokenStatus => {
  return { payload: tokenStatus, type: TOKEN_ACTIONS.CHANGE_TOKEN_STATUS }
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
