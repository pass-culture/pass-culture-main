import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'
import withLogin from './with-login'

import { getRedirectToCurrentLocationOrDiscovery } from './helpers'
import withFrenchQueryRouter from '../withFrenchQueryRouter'

export const handleSuccess = (state, action, ownProps) => {
  const {
    payload: { datum },
  } = action
  const { history, location } = ownProps
  const redirect = getRedirectToCurrentLocationOrDiscovery({
    currentUser: datum,
    ...location,
  })

  if (redirect) {
    history.push(redirect)
  }
}

const withNotRequiredLogin = compose(
  withFrenchQueryRouter,
  withLogin({
    handleSuccess,
    isRequired: false,
    requestData,
  })
)

export default withNotRequiredLogin
