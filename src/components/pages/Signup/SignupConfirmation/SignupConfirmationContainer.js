import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { connect } from 'react-redux'
import SignupConfirmation from './SignupConfirmation'

export default compose(
  withRouter,
  connect()
)(SignupConfirmation)
