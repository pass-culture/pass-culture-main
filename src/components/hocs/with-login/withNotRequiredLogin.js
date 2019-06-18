import withLogin from 'with-react-redux-login'
import { compose } from 'redux'

import { getRedirectToCurrentLocationOrDiscovery } from './helpers'
import withFrenchQueryRouter from '../withFrenchQueryRouter'

const withNotRequiredLogin = compose(
  withFrenchQueryRouter,
  withLogin({
    handleSuccess: (state, { payload: { datum } }, { history, location }) =>
      history.push(
        getRedirectToCurrentLocationOrDiscovery({
          currentUser: datum,
          ...location,
        })
      ),
    isRequired: false,
  })
)

export default withNotRequiredLogin
