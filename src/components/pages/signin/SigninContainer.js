import { connect } from 'react-redux'
import { compose } from 'redux'
import withQueryRouter from 'with-query-router'

import Signin from './Signin'
import { withRedirectToDiscoveryOrTypeformAfterLogin } from '../../hocs'

const SigninContainer = compose(
  withRedirectToDiscoveryOrTypeformAfterLogin,
  withQueryRouter,
  connect()
)(Signin)

export default SigninContainer
