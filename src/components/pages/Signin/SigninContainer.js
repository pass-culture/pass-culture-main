import {compose} from "redux"

import Signin from './Signin'
import {withFrenchQueryRouter} from "../../hocs"
import {withRedirectToOffersWhenAlreadyAuthenticated} from "../../hocs/with-login"

export default compose(
  withRedirectToOffersWhenAlreadyAuthenticated,
  withFrenchQueryRouter
)(Signin)
