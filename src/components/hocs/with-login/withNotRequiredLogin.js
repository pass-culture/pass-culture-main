import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import { getRedirectToCurrentLocationOrDiscovery } from './helpers'
import withLogin from './withLogin'

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
  withRouter,
  withLogin({
    handleSuccess,
    isRequired: false,
    requestData,
  })
)

export default withNotRequiredLogin
