import withLogin from 'with-react-redux-login'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import {
  getRedirectToSignin,
  getRedirectToCurrentLocationOrTypeform,
} from './helpers'

const withRedirectToSigninOrTypeformAfterLogin = compose(
  withRouter,
  withLogin({
    handleFail: (state, action, { history, location }) =>
      history.push(getRedirectToSignin(location)),
    handleSuccess: (state, action, { currentUser, history, location }) =>
      history.push(
        getRedirectToCurrentLocationOrTypeform({
          currentUser,
          ...location,
        })
      ),
    isRequired: true,
  })
)

export default withRedirectToSigninOrTypeformAfterLogin
