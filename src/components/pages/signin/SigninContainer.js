import { connect } from 'react-redux'
import { compose } from 'redux'

import Signin from './Signin'
import { withNotRequiredLogin } from '../../hocs'

const SigninContainer = compose(
  withNotRequiredLogin,
  connect()
)(Signin)

export default SigninContainer
