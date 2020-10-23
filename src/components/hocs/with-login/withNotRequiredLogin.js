import { compose } from 'redux'

import withFrenchQueryRouter from '../withFrenchQueryRouter'

import { getRedirectToOffersOrOfferers } from './helpers'
import withLogin from './withLogin'


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
