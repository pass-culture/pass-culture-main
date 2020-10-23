import { compose } from 'redux'

import withFrenchQueryRouter from '../withFrenchQueryRouter'

import { getRedirectToSignin } from './helpers'
import withLogin from './withLogin'


const withRequiredLogin = compose(
  withFrenchQueryRouter,
  withLogin({
    handleFail: (state, action, ownProps) => {
      const { history, location } = ownProps
      history.push(getRedirectToSignin({ ...location }))
    },
    isRequired: true,
  })
)

export default withRequiredLogin
