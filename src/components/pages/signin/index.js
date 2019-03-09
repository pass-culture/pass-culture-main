import { compose } from 'redux'
import { connect } from 'react-redux'
import withQueryRouter from 'with-query-router'

import SigninContent from './SigninContent'
import { withRedirectToDiscoveryWhenAlreadyAuthenticated } from '../../hocs'

export const Signin = compose(
  withRedirectToDiscoveryWhenAlreadyAuthenticated,
  withQueryRouter,
  connect()
)(SigninContent)

export default Signin
