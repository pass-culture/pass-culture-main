import { compose } from 'redux'
import { connect } from 'react-redux'
import { SignupValidation } from './SignupValidation'

export default compose(
  withRouter,
  connect()
)(SignupValidation)
