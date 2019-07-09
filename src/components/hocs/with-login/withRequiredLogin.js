import { compose } from 'redux'
import withLogin from 'with-react-redux-login'

import { getRedirectToSignin } from './helpers'
import withFrenchQueryRouter from '../withFrenchQueryRouter'

const withRequiredLogin = compose(
  withFrenchQueryRouter,
  withLogin({
    handleFail: (state, action, ownProps) => {
      const { history, location } = ownProps
      history.push(getRedirectToSignin({...location}))
    },
    isRequired: true,
  })
)

export default withRequiredLogin
