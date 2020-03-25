import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'
import withLogin from './withLogin'

import withFrenchQueryRouter from '../withFrenchQueryRouter'
import { getRedirectToSignin, getRedirectToCurrentLocationOrTypeform } from './helpers'

export const handleFail = (state, action, ownProps) => {
  const { history, location } = ownProps
  history.push(getRedirectToSignin(location))
}

export const handleSuccess = (state, action, ownProps) => {
  const {
    payload: { datum },
  } = action
  const { history, location } = ownProps
  const redirect = getRedirectToCurrentLocationOrTypeform({
    currentUser: datum,
    ...location,
  })

  if (redirect) {
    history.push(redirect)
  }
}

const withRequiredLogin = compose(
  withFrenchQueryRouter,
  withLogin({
    handleFail,
    handleSuccess,
    isRequired: true,
    requestData,
  })
)

export default withRequiredLogin
