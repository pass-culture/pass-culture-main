import { connect } from 'react-redux'
import { compose } from 'redux'

import Signin from './Signin'
import { withRedirectToDiscoveryOrTypeformAfterLogin } from '../../hocs'

const SigninContainer = compose(
  withRedirectToDiscoveryOrTypeformAfterLogin,
  connect()
)(Signin)

export default SigninContainer
