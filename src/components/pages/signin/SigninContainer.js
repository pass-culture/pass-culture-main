import { connect } from 'react-redux'
import { compose } from 'redux'

import Signin from './Signin'
import {
  withFrenchQueryRouter,
  withRedirectToDiscoveryOrTypeformAfterLogin,
} from '../../hocs'

const SigninContainer = compose(
  withRedirectToDiscoveryOrTypeformAfterLogin,
  withFrenchQueryRouter,
  connect()
)(Signin)

export default SigninContainer
