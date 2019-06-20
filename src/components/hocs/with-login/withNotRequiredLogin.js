import { compose } from 'redux'
import withLogin from 'with-react-redux-login'

import { getRedirectToCurrentLocationOrDiscovery } from './helpers'
import withFrenchQueryRouter from '../withFrenchQueryRouter'

const withNotRequiredLogin = compose(
  withFrenchQueryRouter,
  withLogin({
    handleSuccess: (state, action, ownProps) => {
      const {
        payload: { datum },
      } = action
      const { history, location } = ownProps
      history.push(
        getRedirectToCurrentLocationOrDiscovery({
          currentUser: datum,
          ...location,
        })
      )
    },
    isRequired: false,
  })
)

export default withNotRequiredLogin
