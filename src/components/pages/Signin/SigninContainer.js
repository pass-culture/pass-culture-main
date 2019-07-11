import { compose } from 'redux'

import Signin from './Signin'
import { withFrenchQueryRouter } from "../../hocs/withFrenchQueryRouter"
import { withNotRequiredLogin } from "../../hocs/with-login"

export default compose(
  withNotRequiredLogin,
  withFrenchQueryRouter
)(Signin)
