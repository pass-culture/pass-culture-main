import { requestData } from 'redux-saga-data'

export const isValidToken = token => {
  const tokenValidityRequest = new Promise((resolve, reject) => {
    requestData({
      apiPath: `/users/token/${token}`,
      handleFail: reject,
      handleSuccess: resolve,
      method: 'GET',
    })
  })

  return tokenValidityRequest.then(() => true).catch(() => false)
}
