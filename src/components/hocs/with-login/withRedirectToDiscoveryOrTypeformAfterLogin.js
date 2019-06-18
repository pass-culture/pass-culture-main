import withLogin from 'with-react-redux-login'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { getRedirectToCurrentLocationOrDiscovery } from './helpers'

const withRedirectToDiscoveryOrTypeformAfterLogin = compose(
  withRouter,
  withLogin({
    handleSuccess: (state, action, { currentUser, history, location }) =>
      history.push(
        getRedirectToCurrentLocationOrDiscovery({
          currentUser,
          ...location,
        })
      ),
    isRequired: false,
  })
)

export default withRedirectToDiscoveryOrTypeformAfterLogin
