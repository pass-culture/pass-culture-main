import { requestData } from 'redux-thunk-data'

import { resolveCurrentUser } from '../../../hocs/with-login/withLogin'

export const updateUser = (formValues, handleSubmitFail, handleSubmitSuccess) =>
  requestData({
    apiPath: 'users/current',
    body: formValues,
    handleFail: handleSubmitFail,
    handleSuccess: handleSubmitSuccess,
    key: 'user',
    method: 'PATCH',
    resolve: resolveCurrentUser,
  })
