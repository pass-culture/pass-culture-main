import { compose } from 'redux'
import withLogin from 'with-react-redux-login'

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
  })
)

export default withNotRequiredLogin
