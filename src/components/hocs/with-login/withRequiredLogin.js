import { compose } from 'redux'
import withLogin from 'with-react-redux-login'

import withFrenchQueryRouter from '../withFrenchQueryRouter'

import {
  getRedirectToSignin,
  getRedirectToCurrentLocationOrTypeform,
} from './helpers'

const withRequiredLogin = compose(
  withFrenchQueryRouter,
  withLogin({
    handleFail: (state, action, { history, location }) =>
      history.push(getRedirectToSignin(location)),
    handleSuccess: (state, { payload: { datum } }, { history, location }) =>
      history.push(
        getRedirectToCurrentLocationOrTypeform({
          currentUser: datum,
          ...location,
        })
      ),
    isRequired: true,
  })
)

export default withRequiredLogin
