import { compose } from 'redux'
import { connect } from 'react-redux'

import SigninContent from './SigninContent'
import { withRedirectToDiscoveryOrTypeformAfterLogin } from '../../hocs'

export const Signin = compose(
  withRedirectToDiscoveryOrTypeformAfterLogin,
  connect()
)(SigninContent)

export default Signin
