import { compose } from 'redux'
import withLogin from './withLogin'

import { getRedirectToOffersOrOfferers } from './helpers'
import withFrenchQueryRouter from '../withFrenchQueryRouter'

const withNotRequiredLogin = compose(
  withFrenchQueryRouter,
  withLogin({
    handleSuccess: (state, action, ownProps) => {
      const {
        payload: { datum: currentUser },
      } = action
      const { history } = ownProps
      history.push(getRedirectToOffersOrOfferers({ ...currentUser }))
    },
    isRequired: false,
  })
)

export default withNotRequiredLogin
