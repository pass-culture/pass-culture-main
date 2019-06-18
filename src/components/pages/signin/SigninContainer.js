import { connect } from 'react-redux'
import { compose } from 'redux'

import Signin from './Signin'
import { withFrenchQueryRouter, withNotRequiredLogin } from '../../hocs'

const SigninContainer = compose(
  withNotRequiredLogin,
  withFrenchQueryRouter,
  connect()
)(Signin)

export default SigninContainer
