import { compose } from 'redux'
import { connect } from 'react-redux'
import SignupValidation from './SignupValidation'
import withRouter from 'react-router-dom/es/withRouter'

export default compose(
  withRouter,
  connect()
)(SignupValidation)
