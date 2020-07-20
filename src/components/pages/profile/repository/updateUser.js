import { requestData } from 'redux-thunk-data'

export const updateUser = (formValues, handleSubmitFail, handleSubmitSuccess) =>
  requestData({
    apiPath: 'users/current',
    body: formValues,
    handleFail: handleSubmitFail,
    handleSuccess: handleSubmitSuccess,
    key: 'user',
    method: 'PATCH',
  })
