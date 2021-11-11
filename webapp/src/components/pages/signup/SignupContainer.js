import { compose } from 'redux'
import { connect } from 'react-redux'
import withNotRequiredLogin from '../../hocs/with-login/withNotRequiredLogin'

import SignUp from './SignUp'

export default compose(
  withNotRequiredLogin,
  connect()
)(SignUp)
