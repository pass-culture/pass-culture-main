import { compose } from 'redux'
import withLogin from 'with-react-redux-login'

import withFrenchQueryRouter from '../withFrenchQueryRouter'

import { getRedirectToSignin, getRedirectToCurrentLocationOrTypeform } from './helpers'

const withRequiredLogin = compose(
  withFrenchQueryRouter,
  withLogin({
    handleFail: (state, action, ownProps) => {
      const { history, location } = ownProps
      history.push(getRedirectToSignin(location))
    },
    handleSuccess: (state, action, ownProps) => {
      const {
        payload: { datum },
      } = action
      const { history, location } = ownProps
      history.push(
        getRedirectToCurrentLocationOrTypeform({
          currentUser: datum,
          ...location,
        })
      )
    },
    isRequired: true,
  })
)

export default withRequiredLogin
