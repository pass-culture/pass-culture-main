import { compose } from 'redux'

import Signin from './Signin'
import withFrenchQueryRouter from '../../hocs/withFrenchQueryRouter'
import { withRedirectToOffersWhenAlreadyAuthenticated } from '../../hocs/with-login/withRedirectToOffersWhenAlreadyAuthenticated'

export default compose(
  withRedirectToOffersWhenAlreadyAuthenticated,
  withFrenchQueryRouter
)(Signin)
